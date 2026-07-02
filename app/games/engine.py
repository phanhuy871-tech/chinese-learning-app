from app.core.exceptions import NotEnoughDataError
from app.games.common.option_generator import build_word_options
from app.games.schemas import GameOption, GameQuestion
from app.sentences.schemas import Sentence
from app.vocabulary.schemas import Word


def build_word_question(
    game_type: str,
    correct: Word,
    candidates: list[Word],
    lesson_order: int,
    question_field: str,
    option_mode: str,
    prompt: str,
    strategy: str = "same_lesson_scope",
    exclude_same_pinyin: bool = False,
) -> GameQuestion:
    """Tạo câu hỏi game ở cấp độ từ vựng.

    Ví dụ:
    - audio_to_hanzi: nghe âm thanh, chọn chữ Hán.
    - hanzi_to_pinyin: nhìn chữ Hán, chọn pinyin.
    - pinyin_to_hanzi: nhìn pinyin, chọn chữ Hán và tránh đáp án cùng cách đọc.
    """
    if len(candidates) < 2:
        raise NotEnoughDataError("Can it nhat 2 tu trong pham vi bai hoc de tao cau hoi.")

    # Tạo 4 đáp án: 1 đáp án đúng + các đáp án nhiễu theo strategy.
    options = build_word_options(
        correct=correct,
        candidates=candidates,
        mode=option_mode,
        strategy=strategy,
        exclude_same_pinyin=exclude_same_pinyin,
    )
    question_value = getattr(correct, question_field)
    return GameQuestion(
        # GameQuestion là format chung frontend hiểu được cho mọi loại game.
        game_type=game_type,
        prompt=prompt,
        lesson_order=lesson_order,
        question_text=question_value if question_field not in {"audio_url"} else "",
        hanzi=correct.hanzi if question_field == "hanzi" else "",
        pinyin=correct.pinyin if question_field == "pinyin" else "",
        meaning_vi=correct.meaning_vi if question_field == "meaning_vi" else "",
        audio_url=correct.audio_url if question_field == "audio_url" else "",
        options=options,
        answer_id=correct.id,
        explanation={
            "hanzi": correct.hanzi,
            "pinyin": correct.pinyin,
            "meaning_vi": correct.meaning_vi,
            "lesson_id": correct.lesson_id,
        },
    )


def build_sentence_ordering(sentence: Sentence) -> GameQuestion:
    """Tạo game sắp xếp câu từ dữ liệu tab câu."""
    # Mỗi từ/mảnh câu trở thành một option. Frontend sẽ cho người học bấm theo thứ tự.
    options = [
        GameOption(id=f"{sentence.id}-{index}", text=word, value=word)
        for index, word in enumerate(sentence.words)
    ]
    return GameQuestion(
        game_type="sentence_ordering",
        prompt="Sap xep lai thanh cau dung",
        lesson_order=sentence.lesson_order,
        question_text=sentence.sentence_vi,
        options=list(reversed(options)),
        answer_id="|".join(sentence.words),
        explanation={
            "sentence_hanzi": sentence.sentence_hanzi,
            "sentence_pinyin": sentence.sentence_pinyin,
            "sentence_vi": sentence.sentence_vi,
        },
    )


def build_sentence_blank(sentence: Sentence, candidate_words: list[Word]) -> GameQuestion:
    """Tạo game điền từ vào chỗ trống.

    Đáp án đúng lấy từ blank_answer_word_id trước, nếu thiếu thì fallback theo chữ Hán.
    Danh sách đáp án nhiễu ưu tiên blank_options_word_ids nếu sheet có khai báo.
    """
    correct = next(
        (word for word in candidate_words if word.id == sentence.blank_answer_word_id),
        None,
    )
    if correct is None:
        correct = next((word for word in candidate_words if word.hanzi == sentence.blank_answer_hanzi), None)
    if correct is None:
        raise NotEnoughDataError("Khong tim thay dap an dung cho cau dien cho trong.")

    # Nếu sheet có cột blank_options_word_ids thì chỉ dùng các từ đó làm đáp án nhiễu.
    allowed_ids = set(sentence.blank_options_word_ids)
    option_candidates = [
        word for word in candidate_words if not allowed_ids or word.id in allowed_ids or word.id == correct.id
    ]
    options = build_word_options(correct, option_candidates, mode="hanzi")
    return GameQuestion(
        game_type="sentence_blank",
        prompt="Chon tu dung voi ngu canh",
        lesson_order=sentence.lesson_order,
        question_text=sentence.blank_sentence,
        options=options,
        answer_id=correct.id,
        explanation={
            "sentence_hanzi": sentence.sentence_hanzi,
            "sentence_pinyin": sentence.sentence_pinyin,
            "sentence_vi": sentence.sentence_vi,
        },
    )
