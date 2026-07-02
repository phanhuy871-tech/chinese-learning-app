import re

from app.data_sources.google_sheets.schema_mapper import (
    GRAMMAR_COLUMNS,
    LESSON_COLUMNS,
    RADICAL_COLUMNS,
    SENTENCE_COLUMNS,
    TOPIC_COLUMNS,
    WORD_COLUMNS,
    pick,
)
from app.learning.lesson_scope import lesson_order_from_value
from app.learning.schemas import GrammarPoint, Lesson, Topic
from app.radicals.schemas import Radical
from app.sentences.schemas import Sentence
from app.vocabulary.schemas import Word

TONE_MARKS = str.maketrans(
    "\u0101\u00e1\u01ce\u00e0\u0113\u00e9\u011b\u00e8\u012b\u00ed\u01d0\u00ec\u014d\u00f3\u01d2\u00f2\u016b\u00fa\u01d4\u00f9\u01d6\u01d8\u01da\u01dc\u00fc",
    "aaaaeeeeiiiioooouuuuvvvvv",
)


def strip_pinyin_tones(value: str) -> str:
    # Bỏ dấu thanh pinyin để so sánh âm gần giống nhau khi tạo đáp án nhiễu.
    return re.sub(r"\s+", " ", value.translate(TONE_MARKS).lower()).strip()


def parse_bool(value: str, default: bool = True) -> bool:
    # Cột is_active trên Sheet có thể ghi 0/false/no/không/tắt để ẩn dữ liệu.
    if not value:
        return default
    return value.strip().lower() not in {"0", "false", "no", "không", "tat", "tắt"}


def parse_int(value: str, default: int = 1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_tags(value: str) -> list[str]:
    # Tags có thể phân tách bằng dấu phẩy, dấu | hoặc dấu ;.
    if not value:
        return []
    return [item.strip() for item in re.split(r"[,|;]", value) if item.strip()]


def parse_list(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in re.split(r"[|,;]", value) if item.strip()]


def resolve_lesson(row: dict[str, str]) -> tuple[str, int]:
    # Chuẩn hóa lesson_id và lesson_order để các tab khác nhau vẫn khớp bài học.
    lesson_id = pick(row, WORD_COLUMNS["lesson_id"])
    lesson_order = parse_int(pick(row, WORD_COLUMNS["lesson_order"]), 0)
    if lesson_order == 0:
        lesson_order = lesson_order_from_value(lesson_id)
    if lesson_order and not lesson_id.startswith("lesson-"):
        lesson_id = f"lesson-{lesson_order}"
    return lesson_id, lesson_order


def parse_words(rows: list[dict[str, str]]) -> list[Word]:
    """Chuyển các dòng tab từ vựng thành danh sách Word.

    Dòng nào thiếu chữ Hán, pinyin hoặc nghĩa tiếng Việt sẽ bị bỏ qua để tránh game lỗi.
    """
    words: list[Word] = []
    for index, row in enumerate(rows, start=1):
        hanzi = pick(row, WORD_COLUMNS["hanzi"])
        pinyin = pick(row, WORD_COLUMNS["pinyin"])
        meaning_vi = pick(row, WORD_COLUMNS["meaning_vi"])
        if not (hanzi and pinyin and meaning_vi):
            continue

        pinyin_no_tone = pick(row, WORD_COLUMNS["pinyin_no_tone"]) or strip_pinyin_tones(pinyin)
        lesson_id, lesson_order = resolve_lesson(row)

        words.append(
            Word(
                id=pick(row, WORD_COLUMNS["id"], f"word-{index}"),
                hanzi=hanzi,
                pinyin=pinyin,
                pinyin_no_tone=pinyin_no_tone,
                meaning_vi=meaning_vi,
                meaning_en=pick(row, WORD_COLUMNS["meaning_en"]),
                word_type=pick(row, WORD_COLUMNS["word_type"]),
                level=pick(row, WORD_COLUMNS["level"]),
                lesson_id=lesson_id,
                lesson_order=lesson_order,
                topic_id=pick(row, WORD_COLUMNS["topic_id"]),
                grammar_ids=parse_list(pick(row, WORD_COLUMNS["grammar_ids"])),
                audio_url=pick(row, WORD_COLUMNS["audio_url"]),
                image_url=pick(row, WORD_COLUMNS["image_url"]),
                decomposition=pick(row, WORD_COLUMNS["decomposition"]),
                example_sentence_hanzi=pick(row, WORD_COLUMNS["example_sentence_hanzi"]),
                example_sentence_pinyin=pick(row, WORD_COLUMNS["example_sentence_pinyin"]),
                example_sentence_vi=pick(row, WORD_COLUMNS["example_sentence_vi"]),
                difficulty=parse_int(pick(row, WORD_COLUMNS["difficulty"]), 1),
                tags=parse_tags(pick(row, WORD_COLUMNS["tags"])),
                is_active=parse_bool(pick(row, WORD_COLUMNS["is_active"]), True),
            )
        )
    return words


def parse_sentences(rows: list[dict[str, str]]) -> list[Sentence]:
    """Chuyển tab câu thành Sentence dùng cho game câu.

    validation_status = needs_content nghĩa là câu chưa đủ nội dung, chưa đưa vào app.
    """
    sentences: list[Sentence] = []
    for index, row in enumerate(rows, start=1):
        sentence_hanzi = pick(row, SENTENCE_COLUMNS["sentence_hanzi"])
        validation_status = pick(row, SENTENCE_COLUMNS["validation_status"], "ready")
        if not sentence_hanzi or validation_status == "needs_content":
            continue

        words = parse_list(pick(row, SENTENCE_COLUMNS["words"]))
        lesson_id, lesson_order = resolve_lesson(row)

        sentences.append(
            Sentence(
                id=pick(row, SENTENCE_COLUMNS["id"], f"sentence-{index}"),
                target_word_id=pick(row, SENTENCE_COLUMNS["target_word_id"]),
                target_hanzi=pick(row, SENTENCE_COLUMNS["target_hanzi"]),
                sentence_slot=parse_int(pick(row, SENTENCE_COLUMNS["sentence_slot"]), 1),
                sentence_hanzi=sentence_hanzi,
                sentence_pinyin=pick(row, SENTENCE_COLUMNS["sentence_pinyin"]),
                sentence_vi=pick(row, SENTENCE_COLUMNS["sentence_vi"]),
                words=words,
                word_ids=parse_list(pick(row, SENTENCE_COLUMNS["word_ids"])),
                blank_sentence=pick(row, SENTENCE_COLUMNS["blank_sentence"]),
                blank_answer_hanzi=pick(row, SENTENCE_COLUMNS["blank_answer_hanzi"]),
                blank_answer_word_id=pick(row, SENTENCE_COLUMNS["blank_answer_word_id"]),
                blank_options_word_ids=parse_list(pick(row, SENTENCE_COLUMNS["blank_options_word_ids"])),
                grammar_point=pick(row, SENTENCE_COLUMNS["grammar_point"]),
                grammar_ids=parse_list(pick(row, SENTENCE_COLUMNS["grammar_ids"])),
                level=pick(row, WORD_COLUMNS["level"]),
                lesson_id=lesson_id,
                lesson_order=lesson_order,
                max_word_lesson_order=parse_int(
                    pick(row, SENTENCE_COLUMNS["max_word_lesson_order"]), lesson_order
                ),
                topic_id=pick(row, WORD_COLUMNS["topic_id"]),
                audio_url=pick(row, WORD_COLUMNS["audio_url"]),
                difficulty=parse_int(pick(row, WORD_COLUMNS["difficulty"]), 1),
                is_active=parse_bool(pick(row, WORD_COLUMNS["is_active"]), True),
                validation_status=validation_status,
                scope_rule=pick(row, SENTENCE_COLUMNS["scope_rule"]),
                note=pick(row, SENTENCE_COLUMNS["note"]),
            )
        )
    return sentences


def parse_lessons(rows: list[dict[str, str]]) -> list[Lesson]:
    # Tạo danh sách bài/nhóm học. seen giúp không tạo trùng lesson khi Sheet có nhiều dòng.
    lessons: list[Lesson] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        lesson_id = pick(row, LESSON_COLUMNS["id"]) or pick(row, WORD_COLUMNS["lesson_id"])
        if not lesson_id or lesson_id in seen:
            continue
        order_index = parse_int(pick(row, LESSON_COLUMNS["order_index"]), 0)
        if order_index == 0:
            order_index = lesson_order_from_value(lesson_id, index)
        lessons.append(
            Lesson(
                id=lesson_id,
                name=pick(row, LESSON_COLUMNS["name"], lesson_id),
                order_index=order_index,
                level=pick(row, LESSON_COLUMNS["level"]),
                description=pick(row, LESSON_COLUMNS["description"]),
                is_active=parse_bool(pick(row, LESSON_COLUMNS["is_active"]), True),
            )
        )
        seen.add(lesson_id)
    return lessons


def parse_topics(rows: list[dict[str, str]]) -> list[Topic]:
    # Topic dùng để phân loại về sau, hiện app mới lưu để mở rộng.
    topics: list[Topic] = []
    seen: set[str] = set()
    for row in rows:
        topic_id = pick(row, TOPIC_COLUMNS["id"]) or pick(row, WORD_COLUMNS["topic_id"])
        if not topic_id or topic_id in seen:
            continue
        topics.append(
            Topic(
                id=topic_id,
                name=pick(row, TOPIC_COLUMNS["name"], topic_id),
                description=pick(row, TOPIC_COLUMNS["description"]),
                is_active=parse_bool(pick(row, TOPIC_COLUMNS["is_active"]), True),
            )
        )
        seen.add(topic_id)
    return topics


def parse_grammar_points(rows: list[dict[str, str]]) -> list[GrammarPoint]:
    # GrammarPoint là kho ngữ pháp, chuẩn bị cho module ngữ pháp sau này.
    grammar_points: list[GrammarPoint] = []
    for index, row in enumerate(rows, start=1):
        grammar_id = pick(row, GRAMMAR_COLUMNS["id"])
        title = pick(row, GRAMMAR_COLUMNS["title_vi"])
        if not (grammar_id or title):
            continue
        lesson_id = pick(row, GRAMMAR_COLUMNS["lesson_id"])
        lesson_order = parse_int(pick(row, GRAMMAR_COLUMNS["lesson_order"]), 0)
        if lesson_order == 0:
            lesson_order = lesson_order_from_value(lesson_id)
        grammar_points.append(
            GrammarPoint(
                id=grammar_id or f"grammar-{index}",
                title_vi=title,
                pattern=pick(row, GRAMMAR_COLUMNS["pattern"]),
                explanation_vi=pick(row, GRAMMAR_COLUMNS["explanation_vi"]),
                example_hanzi=pick(row, GRAMMAR_COLUMNS["example_hanzi"]),
                example_pinyin=pick(row, GRAMMAR_COLUMNS["example_pinyin"]),
                example_vi=pick(row, GRAMMAR_COLUMNS["example_vi"]),
                level=pick(row, GRAMMAR_COLUMNS["level"]),
                lesson_id=lesson_id,
                lesson_order=lesson_order,
                tags=parse_tags(pick(row, GRAMMAR_COLUMNS["tags"])),
                is_active=parse_bool(pick(row, GRAMMAR_COLUMNS["is_active"]), True),
            )
        )
    return grammar_points


def parse_radicals(rows: list[dict[str, str]]) -> list[Radical]:
    # Parse tab bộ thủ. Nếu ô bộ thủ có dạng "人 / 亻" thì tách thành variants.
    radicals: list[Radical] = []
    for index, row in enumerate(rows, start=1):
        radical_value = pick(row, RADICAL_COLUMNS["radical"])
        if not radical_value:
            continue
        variants = parse_list(radical_value.replace(" / ", "|").replace("/", "|"))
        radicals.append(
            Radical(
                id=pick(row, RADICAL_COLUMNS["id"], f"radical-{index}"),
                radical=variants[0] if variants else radical_value,
                variants=variants,
                pinyin=pick(row, RADICAL_COLUMNS["pinyin"]),
                han_viet=pick(row, RADICAL_COLUMNS["han_viet"]),
                meaning_vi=pick(row, RADICAL_COLUMNS["meaning_vi"]),
                memory_tip=pick(row, RADICAL_COLUMNS["memory_tip"]),
                semantic_note=pick(row, RADICAL_COLUMNS["semantic_note"]),
                common_words=parse_list(pick(row, RADICAL_COLUMNS["common_words"])),
                is_active=parse_bool(pick(row, RADICAL_COLUMNS["is_active"]), True),
            )
        )
    return radicals
