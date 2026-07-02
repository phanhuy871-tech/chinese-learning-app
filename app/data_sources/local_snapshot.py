import csv
from pathlib import Path

from app.data_sources.google_sheets.parser import (
    parse_grammar_points,
    parse_lessons,
    parse_radicals,
    parse_sentences,
    parse_topics,
    parse_words,
)
from app.database.repository import repository
from app.learning.schemas import Lesson
from app.sentences.schemas import Sentence
from app.vocabulary.schemas import Word

SNAPSHOT_DIR = Path("data/local")

SENTENCE_VI_REPAIRS = {
    "请问，您贵姓？": "Xin hỏi, ngài họ gì?",
    "我问老师。": "Tôi hỏi thầy/cô giáo.",
    "您贵姓？": "Ngài họ gì?",
    "我姓王。": "Tôi họ Vương.",
    "我叫小明。": "Tôi tên là Tiểu Minh.",
    "你的名字是什么？": "Tên của bạn là gì?",
    "你是哪国人？": "Bạn là người nước nào?",
    "我认识他。": "Tôi quen anh ấy.",
    "认识你很高兴。": "Rất vui được biết bạn.",
    "我也学习汉语。": "Tôi cũng học tiếng Hán.",
    "他们学习汉语。": "Họ học tiếng Hán.",
    "这是什么？": "Đây là cái gì?",
    "这个字怎么发音？": "Chữ này phát âm thế nào?",
    "我学习汉字。": "Tôi học chữ Hán.",
    "这是谁的书？": "Đây là sách của ai?",
    "谁是老师？": "Ai là giáo viên?",
    "这是我的书。": "Đây là sách của tôi.",
    "这是汉语杂志。": "Đây là tạp chí tiếng Hán.",
    "我学习中文。": "Tôi học tiếng Trung.",
}


def supplement_lessons_from_words(lessons: list[Lesson], words: list[Word]) -> list[Lesson]:
    # Neu tab lessons thieu "Nhom 6" nhung tab tu vung co lesson_order=6,
    # ham nay tu tao Lesson tu du lieu tu vung de giao dien khong bi thieu bai.
    lesson_by_order = {lesson.order_index: lesson for lesson in lessons}
    for word in words:
        if word.lesson_order and word.lesson_order not in lesson_by_order:
            lesson_by_order[word.lesson_order] = Lesson(
                id=f"lesson-{word.lesson_order}",
                name=f"Nhóm {word.lesson_order}",
                order_index=word.lesson_order,
                level=word.level,
                description=f"Từ vựng nhóm {word.lesson_order}",
            )
    return [lesson_by_order[key] for key in sorted(lesson_by_order)]


def repair_snapshot_sentences(sentences: list[Sentence]) -> list[Sentence]:
    # Một số câu auto_from_vocab_example trong snapshot local bị lệch nghĩa tiếng Việt.
    # Hàm này sửa theo câu Hán trước khi đưa vào game, để người học không thấy giải thích sai.
    repaired: list[Sentence] = []
    for sentence in sentences:
        fixed_vi = SENTENCE_VI_REPAIRS.get(sentence.sentence_hanzi)
        if fixed_vi:
            repaired.append(sentence.model_copy(update={"sentence_vi": fixed_vi}))
        else:
            repaired.append(sentence)
    return repaired


def read_tsv(name: str) -> list[dict[str, str]]:
    # Doc file snapshot local, vi backend Python chua dang nhap Google nhu trinh duyet.
    # Cac file nay duoc copy tu Google Sheet va luu trong data/local/*.tsv.
    path = SNAPSHOT_DIR / f"{name}.tsv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [
            {key.strip(): (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(file, delimiter="\t")
        ]


def load_local_snapshot() -> dict[str, int] | None:
    # Nap toan bo du lieu local snapshot vao repository trong bo nho.
    # Tra ve thong ke so dong/so ban ghi de API /sync hien cho nguoi dung.
    words_rows = read_tsv("words")
    if not words_rows:
        return None

    sentences_rows = read_tsv("sentences")
    grammar_rows = read_tsv("grammar")
    lessons_rows = read_tsv("lessons") or words_rows
    topics_rows = read_tsv("topics") or words_rows
    radical_rows = read_tsv("radicals")

    words = parse_words(words_rows)
    sentences = repair_snapshot_sentences(parse_sentences(sentences_rows))
    lessons = parse_lessons(lessons_rows)
    topics = parse_topics(topics_rows)
    grammar_points = parse_grammar_points(grammar_rows)
    radicals = parse_radicals(radical_rows)
    lessons = supplement_lessons_from_words(lessons, words)

    repository.replace_words(words)
    repository.replace_sentences(sentences)
    repository.replace_lessons(lessons)
    repository.replace_topics(topics)
    repository.replace_grammar_points(grammar_points)
    repository.replace_radicals(radicals)

    return {
        "word_rows": len(words_rows),
        "sentence_rows": len(sentences_rows),
        "grammar_rows": len(grammar_rows),
        "radical_rows": len(radical_rows),
        "words": len(words),
        "sentences": len(sentences),
        "lessons": len(lessons),
        "topics": len(topics),
        "grammar_points": len(grammar_points),
        "radicals": len(radicals),
    }
