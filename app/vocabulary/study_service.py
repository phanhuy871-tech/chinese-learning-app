from app.radicals.schemas import Radical
from app.sentences.schemas import Sentence
from app.vocabulary.schemas import Word


def radicals_for_word(word: Word, radicals: list[Radical]) -> list[Radical]:
    # Tim bo thu lien quan bang 2 cach:
    # 1. Bo thu/ban the xuat hien trong chu Han hoac cot chiet tu.
    # 2. Tu vung nam trong danh sach common_words cua bo thu.
    haystack = f"{word.hanzi} {word.decomposition}"
    matched: list[Radical] = []
    for radical in radicals:
        variants = radical.variants or [radical.radical]
        variant_hit = any(variant and variant in haystack for variant in variants)
        common_word_hit = any(item and item in word.hanzi for item in radical.common_words)
        if variant_hit or common_word_hit:
            matched.append(radical)
    return matched


def sentences_for_word(word: Word, sentences: list[Sentence]) -> list[Sentence]:
    # Tim cac cau vi du lien quan den tu dang hoc.
    # Uu tien target_word_id, nhung van bat duoc cau co word_id hoac co hanzi trong cau.
    return [
        sentence
        for sentence in sentences
        if sentence.target_word_id == word.id or word.id in sentence.word_ids or word.hanzi in sentence.sentence_hanzi
    ]


def build_study_card(word: Word, radicals: list[Radical], sentences: list[Sentence]) -> dict:
    # Day la cau truc frontend can de hien 1 the hoc tu vung.
    return {
        "word": word,
        "radicals": radicals_for_word(word, radicals),
        "sentences": sentences_for_word(word, sentences),
    }
