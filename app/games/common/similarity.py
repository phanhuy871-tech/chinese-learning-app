from app.vocabulary.schemas import Word


def pinyin_similarity_score(left: str, right: str) -> int:
    left_parts = left.lower().split()
    right_parts = right.lower().split()
    score = 0
    if len(left_parts) == len(right_parts):
        score += 3
    for left_part, right_part in zip(left_parts, right_parts):
        if left_part == right_part:
            score += 5
        elif left_part[:1] == right_part[:1]:
            score += 2
        if left_part[-2:] == right_part[-2:]:
            score += 2
        elif left_part[-1:] == right_part[-1:]:
            score += 1
    return score


def sort_by_similar_pinyin(correct: Word, candidates: list[Word]) -> list[Word]:
    return sorted(
        candidates,
        key=lambda word: pinyin_similarity_score(correct.pinyin_no_tone, word.pinyin_no_tone),
        reverse=True,
    )

