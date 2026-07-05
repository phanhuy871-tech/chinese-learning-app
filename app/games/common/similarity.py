from difflib import SequenceMatcher

from app.vocabulary.schemas import Word


PINYIN_CHAR_INFO = {
    "ā": ("a", 1),
    "á": ("a", 2),
    "ǎ": ("a", 3),
    "à": ("a", 4),
    "ē": ("e", 1),
    "é": ("e", 2),
    "ě": ("e", 3),
    "è": ("e", 4),
    "ī": ("i", 1),
    "í": ("i", 2),
    "ǐ": ("i", 3),
    "ì": ("i", 4),
    "ō": ("o", 1),
    "ó": ("o", 2),
    "ǒ": ("o", 3),
    "ò": ("o", 4),
    "ū": ("u", 1),
    "ú": ("u", 2),
    "ǔ": ("u", 3),
    "ù": ("u", 4),
    "ǖ": ("v", 1),
    "ǘ": ("v", 2),
    "ǚ": ("v", 3),
    "ǜ": ("v", 4),
    "ü": ("v", 0),
}


def pinyin_signature(value: str) -> tuple[str, tuple[int, ...]]:
    """Tách pinyin thành phần âm không dấu và chuỗi thanh điệu.

    Ví dụ: qǐng -> ("qing", (3,)); qīng -> ("qing", (1,)).
    """
    base: list[str] = []
    tones: list[int] = []
    for char in str(value or "").casefold():
        if char in PINYIN_CHAR_INFO:
            plain, tone = PINYIN_CHAR_INFO[char]
            base.append(plain)
            if tone:
                tones.append(tone)
            continue
        if char.isascii() and char.isalpha():
            base.append(char)
    return "".join(base), tuple(tones)


def pinyin_option_key(value: str) -> str:
    """Khóa giữ nguyên dấu thanh để loại lựa chọn hiển thị trùng hệt."""
    return "".join(str(value or "").casefold().split())


def pinyin_similarity_score(left: str, right: str) -> int:
    left_base, left_tones = pinyin_signature(left)
    right_base, right_tones = pinyin_signature(right)
    if not left_base or not right_base:
        return 0

    similarity = round(SequenceMatcher(None, left_base, right_base).ratio() * 100)
    score = similarity

    # Cùng âm nhưng khác thanh điệu là đáp án nhiễu tốt nhất.
    if left_base == right_base and left_tones != right_tones:
        score += 1000
    elif left_base == right_base:
        score += 500

    # Sau đó ưu tiên cùng âm đầu hoặc cùng vần.
    if left_base[:1] == right_base[:1]:
        score += 30
    if left_base[-2:] == right_base[-2:]:
        score += 25
    elif left_base[-1:] == right_base[-1:]:
        score += 10
    return score


def sort_by_similar_pinyin(correct: Word, candidates: list[Word]) -> list[Word]:
    return sorted(
        candidates,
        key=lambda word: pinyin_similarity_score(correct.pinyin, word.pinyin),
        reverse=True,
    )
