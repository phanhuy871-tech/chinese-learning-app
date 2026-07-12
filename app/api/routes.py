from fastapi import APIRouter, HTTPException, Response

from app.audio.tts_service import synthesize_chinese_audio
from app.core.exceptions import DataSyncError, NotEnoughDataError
from app.database.repository import repository
from app.data_sources.bootstrap import load_sample_data
from app.data_sources.google_sheets.sync_service import sync_google_sheet
from app.data_sources.local_snapshot import load_local_snapshot
from app.games.registry import build_game_question, game_item_count, list_game_types
from app.users.progress_store import (
    create_user,
    get_progress,
    list_users,
    reset_progress,
    save_progress,
)
from app.vocabulary.study_service import build_study_card

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    """Health check cho môi trường deploy online.

    Các nền tảng như Render/Railway/Fly có thể gọi endpoint này để biết app còn chạy.
    Trả thêm số lượng dữ liệu để mình kiểm tra nhanh app đã nạp Sheet/snapshot chưa.
    """
    return {
        "status": "ok",
        "words": len(repository.list_words()),
        "sentences": len(repository.list_sentences()),
        "grammar_points": len(repository.list_grammar_points()),
        "radicals": len(repository.list_radicals()),
        "lessons": len(repository.list_lessons()),
    }


@router.get("/tts")
async def tts_audio(text: str):
    """Tạo file MP3 phát âm tiếng Trung cho từ/câu đang học."""
    try:
        audio = await synthesize_chinese_audio(text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Chưa tạo được âm thanh TTS.") from exc

    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=604800"},
    )


@router.get("/users")
def users():
    # Danh sách người học nhỏ, mặc định có 10 hồ sơ cho lớp/nhóm nhỏ.
    return list_users()


@router.post("/users")
def add_user(payload: dict[str, str]):
    # Tạo thêm hồ sơ người học nếu cần nhiều hơn 10 người.
    return create_user(payload.get("name", ""))


@router.get("/users/{user_id}/progress")
def user_progress(user_id: str):
    # Lấy tiến độ riêng của một người học.
    return get_progress(user_id)


@router.put("/users/{user_id}/progress")
def update_user_progress(user_id: str, progress: dict):
    # Lưu tiến độ riêng của một người học.
    return save_progress(user_id, progress)


@router.post("/users/{user_id}/progress/reset")
def reset_user_progress(user_id: str):
    # Xóa tiến độ học của một người, không xóa hồ sơ người học.
    return reset_progress(user_id)


@router.post("/sync")
def sync_sheet() -> dict[str, int | str]:
    """Đồng bộ dữ liệu học từ Google Sheet hoặc snapshot local."""
    # Nút "Đồng bộ Sheet" trên giao diện sẽ gọi API này.
    # API ưu tiên đọc Google Sheet online, rồi fallback về snapshot local, cuối cùng là sample data.
    try:
        result = sync_google_sheet()
    except DataSyncError as exc:
        local_result = load_local_snapshot()
        if local_result:
            return {
                "status": "local_snapshot_loaded",
                "reason": str(exc),
                **local_result,
            }
        load_sample_data()
        return {"status": "sample_data_loaded", "reason": str(exc)}
    return {"status": "ok", **result}


@router.get("/lessons")
def lessons():
    # Trả danh sách bài/nhóm để frontend hiện bên cột "Bài học".
    return repository.list_lessons()


@router.get("/topics")
def topics():
    return repository.list_topics()


@router.get("/words")
def words(lesson_order: int | None = None):
    # Nếu không truyền lesson_order: trả toàn bộ từ vựng.
    # Nếu có lesson_order: trả từ vựng trong phạm vi bài đó.
    if lesson_order is None:
        return repository.list_words()
    return repository.list_words_for_lesson(lesson_order)


@router.get("/study/vocabulary")
def study_vocabulary(lesson_order: int = 1):
    """Module 1: học từ vựng theo bài đang chọn."""
    # Chỉ lấy từ đúng bài đang chọn, vì người học muốn học theo nhóm/bài riêng.
    words_for_lesson = [
        word for word in repository.list_words() if word.lesson_order == lesson_order
    ]

    # Mỗi "study card" gồm: từ vựng + bộ thủ liên quan + câu ví dụ sẵn sàng.
    return [
        build_study_card(word, repository.list_radicals(), repository.list_sentences())
        for word in words_for_lesson
    ]


@router.get("/radicals")
def radicals():
    # Trả kho kiến thức bộ thủ đọc từ tab "bộ thủ".
    return repository.list_radicals()


@router.get("/grammar")
def grammar(lesson_order: int | None = None):
    """Trả điểm ngữ pháp.

    Nếu truyền lesson_order thì chỉ lấy ngữ pháp đúng bài đang chọn.
    Nếu không truyền thì trả toàn bộ kho ngữ pháp.
    """
    grammar_points = repository.list_grammar_points()
    if lesson_order is None:
        return grammar_points
    return [
        grammar_point
        for grammar_point in grammar_points
        if grammar_point.lesson_order == lesson_order
    ]


@router.get("/sentences")
def sentences(lesson_order: int | None = None):
    # API phụ để kiểm tra kho câu hoặc debug game câu.
    if lesson_order is None:
        return repository.list_sentences()
    return repository.list_sentences_for_lesson(lesson_order)


@router.get("/games")
def games():
    # Trả danh sách mã game. Trang HTML dùng metadata từ web route để hiển thị đẹp hơn.
    return {"game_types": list_game_types()}


@router.get("/games/{game_type}/session")
def game_session(game_type: str, lesson_order: int = 1):
    # Tra ve so muc trong mot phien choi de frontend tron thu tu va theo doi hoan thanh.
    try:
        return {"game_type": game_type, "lesson_order": lesson_order, "item_count": game_item_count(game_type, lesson_order)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/games/{game_type}/question")
def game_question(game_type: str, lesson_order: int = 1, item_index: int = 0):
    # Tạo 1 câu hỏi game theo loại game và bài đang chọn.
    try:
        return build_game_question(game_type, lesson_order, item_index)
    except (NotEnoughDataError, ZeroDivisionError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
