from random import Random

from app.games.common.similarity import sort_by_similar_pinyin
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
    else:
        pool = sorted(pool, key=lambda word: (word.lesson_order, word.id))

    selected = [correct] + pool[: max(total - 1, 0)]
    options = [word_option(word, mode) for word in selected]
    Random(correct.id).shuffle(options)
    return options
