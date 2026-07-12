from app.database.repository import repository
from app.games.engine import (
    build_sentence_blank,
    build_sentence_ordering,
    build_sentence_translation,
    build_word_question,
)


# Cấu hình các game từ vựng.
# Mỗi dòng mô tả:
# 1. field dùng làm câu hỏi
# 2. kiểu đáp án
# 3. prompt đưa cho người học
# 4. cách chọn đáp án nhiễu
# 5. có loại trừ từ cùng pinyin hay không
WORD_GAME_CONFIG = {
    "audio_to_hanzi": ("audio_url", "hanzi", "Nghe am thanh, chon chu Han dung", "same_lesson_scope", False),
    "audio_to_pinyin": ("audio_url", "pinyin", "Nghe am thanh, chon pinyin dung", "similar_pinyin", False),
    "audio_to_meaning": ("audio_url", "meaning", "Nghe am thanh, chon nghia dung", "same_lesson_scope", False),
    "hanzi_to_audio": ("hanzi", "audio", "Nhin chu Han, chon am thanh dung", "same_lesson_scope", False),
    "hanzi_to_pinyin": ("hanzi", "pinyin", "Nhin chu Han, chon pinyin dung", "same_lesson_scope", False),
    "hanzi_to_meaning": ("hanzi", "meaning", "Nhin chu Han, chon nghia dung", "same_lesson_scope", False),
    "meaning_to_hanzi": ("meaning_vi", "hanzi", "Nhin nghia tieng Viet, chon chu Han dung", "same_lesson_scope", False),
    "pinyin_to_hanzi": ("pinyin", "hanzi", "Nhin pinyin, chon chu Han dung", "same_lesson_scope", True),
    "pinyin_to_meaning": ("pinyin", "meaning", "Nhin pinyin, chon nghia dung", "same_lesson_scope", False),
}

# Metadata chỉ dùng cho giao diện: tên tiếng Việt, mô tả, nhóm kỹ năng.
# Tách metadata khỏi logic giúp sau này đổi chữ trên UI mà không ảnh hưởng engine game.
GAME_META = {
    "audio_to_hanzi": {
        "label": "Nghe chọn chữ Hán",
        "description": "Nghe âm thanh rồi chọn chữ Hán đúng.",
        "group": "Nghe",
    },
    "audio_to_pinyin": {
        "label": "Nghe chọn pinyin",
        "description": "Nghe âm thanh rồi chọn pinyin gần âm, dễ nhầm.",
        "group": "Nghe",
    },
    "audio_to_meaning": {
        "label": "Nghe chọn nghĩa",
        "description": "Nghe âm thanh rồi chọn nghĩa tiếng Việt.",
        "group": "Nghe",
    },
    "hanzi_to_audio": {
        "label": "Nhìn chữ chọn âm",
        "description": "Nhìn chữ Hán rồi chọn âm thanh đúng.",
        "group": "Chữ Hán",
    },
    "hanzi_to_pinyin": {
        "label": "Nhìn chữ chọn pinyin",
        "description": "Nhìn chữ Hán rồi chọn pinyin đúng.",
        "group": "Chữ Hán",
    },
    "hanzi_to_meaning": {
        "label": "Nhìn chữ chọn nghĩa",
        "description": "Nhìn chữ Hán rồi chọn nghĩa đúng.",
        "group": "Chữ Hán",
    },
    "meaning_to_hanzi": {
        "label": "Dịch từ Việt -> Trung",
        "description": "Nhìn nghĩa tiếng Việt rồi chọn từ tiếng Trung đúng.",
        "group": "Dịch",
    },
    "pinyin_to_hanzi": {
        "label": "Nhìn pinyin chọn chữ",
        "description": "Nhìn pinyin rồi chọn chữ Hán, tránh từ cùng cách đọc.",
        "group": "Pinyin",
    },
    "pinyin_to_meaning": {
        "label": "Nhìn pinyin chọn nghĩa",
        "description": "Nhìn pinyin rồi chọn nghĩa tiếng Việt.",
        "group": "Pinyin",
    },
    "sentence_ordering": {
        "label": "Sắp xếp câu",
        "description": "Kéo/chọn các mảnh từ để xếp thành câu đúng.",
        "group": "Câu",
    },
    "sentence_blank": {
        "label": "Điền từ vào câu",
        "description": "Chọn từ phù hợp với ngữ cảnh và chỗ trống.",
        "group": "Câu",
    },
    "sentence_vi_to_hanzi": {
        "label": "Dịch câu Việt -> Trung",
        "description": "Nhìn nghĩa tiếng Việt rồi chọn câu tiếng Trung đúng.",
        "group": "Dịch",
    },
}


def list_game_types() -> list[str]:
    # Thứ tự trong list này cũng là thứ tự hiển thị game trên giao diện.
    return [*WORD_GAME_CONFIG.keys(), "sentence_ordering", "sentence_blank", "sentence_vi_to_hanzi"]


def list_game_metadata() -> list[dict[str, str]]:
    # Frontend cần id để gọi API, label/description/group để hiển thị cho người học.
    return [
        {"id": game_type, **GAME_META[game_type]}
        for game_type in list_game_types()
    ]


def game_item_count(game_type: str, lesson_order: int) -> int:
    """Dem so muc can hoan thanh trong mot phien choi.

    Frontend dung con so nay de tron thu tu cau hoi va dam bao moi muc chi bien mat
    khoi hang doi khi nguoi hoc tra loi dung.
    """
    words = repository.list_words_for_lesson(lesson_order)
    sentences = repository.list_sentences_for_lesson(lesson_order)
    if game_type in WORD_GAME_CONFIG:
        target_words = [word for word in words if word.lesson_order == lesson_order] or words
        return len(target_words)
    if game_type in {"sentence_ordering", "sentence_blank", "sentence_vi_to_hanzi"}:
        return len(sentences)
    raise ValueError(f"Unknown game type: {game_type}")


def build_game_question(game_type: str, lesson_order: int, item_index: int = 0):
    """Router logic của game.

    API truyền vào game_type, hàm này quyết định nên gọi engine tạo câu hỏi từ vựng,
    câu sắp xếp, hay câu điền từ. Nhờ vậy API route rất ngắn và dễ đọc.
    """
    words = repository.list_words_for_lesson(lesson_order)
    sentences = repository.list_sentences_for_lesson(lesson_order)

    if game_type in WORD_GAME_CONFIG:
        # Với game từ vựng:
        # - Đáp án đúng ưu tiên lấy từ đúng bài đang chọn.
        # - Đáp án nhiễu vẫn được lấy trong phạm vi bài 1 -> bài đang chọn.
        # Nhờ vậy chọn Nhóm 6 sẽ luyện từ Nhóm 6, không bắt đầu lại từ Nhóm 1.
        question_field, option_mode, prompt, strategy, exclude_same_pinyin = WORD_GAME_CONFIG[game_type]
        target_words = [word for word in words if word.lesson_order == lesson_order] or words
        correct = target_words[item_index % len(target_words)]
        return build_word_question(
            game_type=game_type,
            correct=correct,
            candidates=words,
            lesson_order=lesson_order,
            question_field=question_field,
            option_mode=option_mode,
            prompt=prompt,
            strategy=strategy,
            exclude_same_pinyin=exclude_same_pinyin,
        )

    # Với game câu, lấy câu theo bài hiện tại và item_index.
    sentence = sentences[item_index % len(sentences)]
    if game_type == "sentence_ordering":
        return build_sentence_ordering(sentence)
    if game_type == "sentence_blank":
        return build_sentence_blank(sentence, words)
    if game_type == "sentence_vi_to_hanzi":
        return build_sentence_translation(sentence, sentences)

    raise ValueError(f"Unknown game type: {game_type}")
