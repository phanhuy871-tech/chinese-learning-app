"""Small reading lessons, separate from the vocabulary lesson catalogue."""
import hashlib
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import quote, urlparse

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.learning.course_glossary import glossary_for
from app.learning.course_tokens import listening_tokens, token_hints
from app.data_sources.google_sheets.client import fetch_public_sheet_rows_by_name

router = APIRouter(prefix="/api/course", tags=["course"])
SNAPSHOT = Path(__file__).resolve().parents[2] / "data/local/course_lessons.json"
STORE = Path(os.environ.get("COURSE_DATA_PATH", str(SNAPSHOT)))
MEDIA = Path(__file__).resolve().parents[1] / "web/static/course-images"
AUDIO_MANIFEST = MEDIA.parent / "course-audio/manifest.json"


def corrected_rows(rows):
    """Apply only the user-approved typo; leave the remote Sheet untouched."""
    result = []
    for source in rows:
        row = dict(source)
        if row.get("sentence_id") == "BK04-C02" and row.get("hanzi") == "那是我的毛，他叫花花":
            row.update(hanzi="那是我的猫，他叫花花",
                       pinyin="nà shì wǒ de māo tā jiào huā huā",
                       translation_vi="Đó là con mèo của tôi, cậu ấy tên là Hoa Hoa.",
                       hint_pinyin="N S W D M T J H H", hint_vi="D L C M C T C A T L H H",
                       source_hanzi=source["hanzi"], audio_refs="")
            row["review_queue"] = "\n\n".join(
                item for item in row.get("review_queue", "").split("\n\n")
                if "SOURCE_TYPO_TRANSLATION" not in item)
        result.append(row)
    return result


def persist_rows(rows):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=STORE.parent,
                                         suffix=".tmp", delete=False) as handle:
            name = handle.name
            json.dump(rows, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, STORE)
    finally:
        if name and Path(name).exists():
            Path(name).unlink()


def media_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if urlparse(value).scheme == "https":
        return value
    if urlparse(value).scheme:
        return ""
    if Path(value).name == value and "\\" not in value and "/" not in value:
        return "/static/course-images/" + quote(value)
    return ""


def parse_course(rows: list[dict]) -> list[dict]:
    lessons, ids = {}, set()
    manifest = json.loads(AUDIO_MANIFEST.read_text(encoding="utf-8")) if AUDIO_MANIFEST.exists() else {}
    for row in rows:
        lesson_id = str(row.get("lesson_id", "")).strip()
        sid = str(row.get("sentence_id", "")).strip()
        hanzi = row.get("hanzi", "")
        if not lesson_id or not sid or not hanzi:
            raise ValueError("Mỗi hàng phải có lesson_id, sentence_id và hanzi.")
        if sid in ids:
            raise ValueError(f"Trùng sentence_id: {sid}")
        ids.add(sid)
        order = int(row.get("sentence_order", 0))
        if order < 1:
            raise ValueError("Thứ tự câu phải lớn hơn 0.")
        sentence = {key: str(row.get(key, "")) for key in (
            "sentence_id", "speaker", "hanzi", "pinyin", "translation_vi",
            "hint_pinyin", "hint_vi", "review_queue", "explanation_vi", "vocabulary",
        )}
        sentence["sentence_order"] = order
        image_ref = row.get("image_refs", "")
        # An explicitly supplied filename/link always wins over the shared lesson image.
        if not image_ref and (MEDIA / f"{lesson_id}.jpg").is_file():
            image_ref = f"{lesson_id}.jpg"
        sentence["image_url"] = media_url(image_ref)
        sentence["audio_url"] = media_url(row.get("audio_refs", ""))
        sentence["audio_segments"] = []
        generated = manifest.get(sid, {})
        if not sentence["audio_url"] and generated.get("text") == hanzi and generated.get("speaker") == sentence["speaker"]:
            sentence["audio_url"] = generated["url"]
            sentence["audio_segments"] = generated.get("segments", [])
        sentence["voice_label"] = "A · giọng nữ Quan thoại" if sentence["speaker"] == "A" else "B · giọng nam Quan thoại" if sentence["speaker"] == "B" else "Quan thoại"
        sentence["word_glossary"] = glossary_for(hanzi)
        sentence["listening_tokens"] = listening_tokens(hanzi)
        sentence["listening_token_hints"] = token_hints(hanzi, sentence["pinyin"])
        sentence["revision"] = hashlib.sha256(json.dumps(
            [hanzi, sentence["pinyin"], sentence["translation_vi"]], ensure_ascii=False,
        ).encode()).hexdigest()
        lesson = lessons.setdefault(lesson_id, {"lesson_id": lesson_id, "sentences": []})
        lesson["sentences"].append(sentence)
    for lesson in lessons.values():
        lesson["sentences"].sort(key=lambda s: s["sentence_order"])
        orders = [s["sentence_order"] for s in lesson["sentences"]]
        if len(orders) != len(set(orders)):
            raise ValueError(f"Trùng thứ tự câu trong {lesson['lesson_id']}")
        lesson["revision"] = hashlib.sha256(json.dumps([
            (s["sentence_id"], s["revision"]) for s in lesson["sentences"]
        ]).encode()).hexdigest()
    return list(lessons.values())


_cached = None


@router.get("/lessons")
def course_lessons():
    global _cached
    if _cached is None:
        path = STORE if STORE.exists() else SNAPSHOT
        _cached = parse_course(corrected_rows(json.loads(path.read_text(encoding="utf-8"))))
    return {"lessons": _cached}


@router.post("/refresh")
def refresh_course():
    global _cached
    try:
        rows = corrected_rows(fetch_public_sheet_rows_by_name(settings.google_sheet_id, "bai khoa"))
        if not rows:
            raise ValueError("Empty sheet; keep existing lessons")
        updated = parse_course(rows)
        persist_rows(rows)
    except Exception as exc:
        raise HTTPException(400, "Không cập nhật được bài khóa. Kiểm tra quyền xem Sheet, ID và thứ tự câu; dữ liệu cũ được giữ nguyên.") from exc
    _cached = updated
    return {"lessons": updated}
