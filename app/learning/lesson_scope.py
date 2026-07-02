import re

from app.sentences.schemas import Sentence
from app.vocabulary.schemas import Word


def lesson_order_from_value(value: str, default: int = 0) -> int:
    if not value:
        return default
    match = re.search(r"\d+", value)
    if not match:
        return default
    return int(match.group(0))


def words_available_for_lesson(words: list[Word], lesson_order: int) -> list[Word]:
    return [
        word
        for word in words
        if word.is_active and (word.lesson_order == 0 or word.lesson_order <= lesson_order)
    ]


def words_in_exact_lesson(words: list[Word], lesson_order: int) -> list[Word]:
    return [word for word in words if word.is_active and word.lesson_order == lesson_order]


def sentence_is_valid_for_lesson(sentence: Sentence, words: list[Word]) -> bool:
    if sentence.lesson_order <= 0:
        return True

    max_allowed = sentence.max_word_lesson_order or sentence.lesson_order
    word_lookup = {word.id: word for word in words}
    for word_id in sentence.word_ids:
        word = word_lookup.get(word_id)
        if word and word.lesson_order > max_allowed:
            return False
    return True

