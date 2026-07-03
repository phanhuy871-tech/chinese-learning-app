from random import Random

from app.games.common.similarity import pinyin_similarity_score, sort_by_similar_pinyin
from app.games.schemas import GameOption
from app.vocabulary.schemas import Word


def word_option(word: Word, mode: str) -> GameOption:
    if mode == "hanzi":
        return GameOption(id=word.id, text=word.hanzi, value=word.hanzi)
    if mode == "pinyin":
        return GameOption(id=word.id, text=word.pinyin, value=word.pinyin)
    if mode == "meaning":
        return GameOption(id=word.id, text=word.meaning_vi, value=word.meaning_vi)
    if mode == "audio":
        # Audio options need both fields:
        # - audio_url: real recorded audio when the sheet has it.
        # - value: hanzi fallback so the browser can speak it with speechSynthesis.
        return GameOption(id=word.id, text="Nghe", audio_url=word.audio_url, value=word.hanzi)
    return GameOption(id=word.id, text=word.hanzi, value=word.hanzi)


def hanzi_length(word: Word) -> int:
    return len(str(word.hanzi or "").strip())


def pinyin_syllable_count(word: Word) -> int:
    source = word.pinyin_no_tone or word.pinyin
    return len([part for part in source.split() if part])


def option_seed(correct: Word, mode: str, strategy: str) -> str:
    return f"{correct.id}:{mode}:{strategy}"


def distractor_score(correct: Word, candidate: Word, strategy: str) -> tuple[int, int, int, int, str]:
    """Chấm điểm đáp án nhiễu để đáp án cùng dạng được ưu tiên hơn.

    Điểm cao hơn nghĩa là phù hợp hơn:
    - cùng số chữ Hán với từ đúng
    - cùng số âm tiết pinyin với từ đúng
    - gần bài hiện tại, tránh cứ lấy từ đầu bài 1
    - nếu game nghe chọn pinyin thì ưu tiên âm gần giống
    """
    same_hanzi_len = int(hanzi_length(candidate) == hanzi_length(correct))
    same_syllables = int(pinyin_syllable_count(candidate) == pinyin_syllable_count(correct))
    lesson_distance = -abs(candidate.lesson_order - correct.lesson_order)
    similar_sound = (
        pinyin_similarity_score(correct.pinyin_no_tone, candidate.pinyin_no_tone)
        if strategy == "similar_pinyin"
        else 0
    )
    return (same_hanzi_len, same_syllables, similar_sound, lesson_distance, candidate.id)


def choose_distractors(
    correct: Word,
    pool: list[Word],
    total: int,
    strategy: str,
    seed: str,
) -> list[Word]:
    """Chọn đáp án nhiễu đa dạng nhưng vẫn cùng dạng với đáp án đúng."""
    needed = max(total - 1, 0)
    if needed <= 0:
        return []

    randomizer = Random(seed)
    shuffled_pool = pool[:]
    randomizer.shuffle(shuffled_pool)
    ranked = sorted(
        shuffled_pool,
        key=lambda word: distractor_score(correct, word, strategy),
        reverse=True,
    )
    return ranked[:needed]


def build_word_options(
    correct: Word,
    candidates: list[Word],
    mode: str,
    total: int = 4,
    strategy: str = "same_lesson_scope",
    exclude_same_pinyin: bool = False,
) -> list[GameOption]:
    pool = [word for word in candidates if word.id != correct.id]
    if exclude_same_pinyin:
        pool = [word for word in pool if word.pinyin_no_tone != correct.pinyin_no_tone]
    if strategy == "similar_pinyin":
        pool = sort_by_similar_pinyin(correct, pool)

    selected = [correct] + choose_distractors(
        correct=correct,
        pool=pool,
        total=total,
        strategy=strategy,
        seed=option_seed(correct, mode, strategy),
    )
    options = [word_option(word, mode) for word in selected]
    Random(option_seed(correct, mode, strategy)).shuffle(options)
    return options
