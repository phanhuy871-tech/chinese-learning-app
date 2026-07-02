WORD_COLUMNS = {
    "id": ["word_id", "id", "ma", "m\u00e3", "stt"],
    "hanzi": ["hanzi", "h\u00e1n t\u1ef1", "han tu", "ch\u1eef h\u00e1n", "chu han", "t\u1eeb", "tu", "word"],
    "pinyin": ["pinyin", "piyin", "phi\u00ean \u00e2m", "phien am"],
    "pinyin_no_tone": ["pinyin_no_tone", "pinyin khong dau", "pinyin kh\u00f4ng d\u1ea5u"],
    "meaning_vi": ["meaning_vi", "ngh\u0129a ti\u1ebfng vi\u1ec7t", "nghia tieng viet", "ngh\u0129a", "nghia"],
    "meaning_en": ["meaning_en", "english"],
    "word_type": ["word_type", "lo\u1ea1i t\u1eeb", "loai tu", "t\u1eeb lo\u1ea1i", "tu loai"],
    "level": ["level", "hsk", "c\u1ea5p \u0111\u1ed9", "cap do"],
    "lesson_id": ["lesson_id", "lesson", "b\u00e0i", "bai", "nh\u00f3m", "nhom"],
    "lesson_order": ["lesson_order", "lesson_number", "s\u1ed1 b\u00e0i", "so bai"],
    "topic_id": ["topic_id", "topic", "ch\u1ee7 \u0111\u1ec1", "chu de"],
    "grammar_ids": ["grammar_ids", "grammar", "ng\u1eef ph\u00e1p", "ngu phap"],
    "audio_url": ["audio_url", "audio", "\u00e2m thanh", "am thanh"],
    "image_url": ["image_url", "image", "\u1ea3nh", "anh"],
    "decomposition": ["decomposition", "chi\u1ebft t\u1eeb", "chiet tu"],
    "example_sentence_hanzi": ["example_sentence_hanzi", "c\u00e2u v\u00ed d\u1ee5", "cau vi du", "v\u00ed d\u1ee5", "vi du"],
    "example_sentence_pinyin": ["example_sentence_pinyin"],
    "example_sentence_vi": ["example_sentence_vi"],
    "difficulty": ["difficulty", "\u0111\u1ed9 kh\u00f3", "do kho"],
    "tags": ["tags", "tag"],
    "is_active": ["is_active", "active", "b\u1eadt", "bat"],
}

SENTENCE_COLUMNS = {
    "id": ["sentence_id", "id c\u00e2u", "id cau"],
    "target_word_id": ["target_word_id"],
    "target_hanzi": ["target_hanzi"],
    "sentence_slot": ["sentence_slot"],
    "sentence_hanzi": ["sentence_hanzi", "c\u00e2u h\u00e1n", "cau han", "sentence"],
    "sentence_pinyin": ["sentence_pinyin", "pinyin c\u00e2u", "pinyin cau"],
    "sentence_vi": ["sentence_vi", "ngh\u0129a c\u00e2u", "nghia cau"],
    "words": ["words", "t\u1eeb trong c\u00e2u", "tu trong cau"],
    "word_ids": ["word_ids", "ids t\u1eeb", "ids tu"],
    "blank_sentence": ["blank_sentence", "c\u00e2u khuy\u1ebft", "cau khuyet"],
    "blank_answer_hanzi": ["blank_answer_hanzi", "\u0111\u00e1p \u00e1n khuy\u1ebft", "dap an khuyet"],
    "blank_answer_word_id": ["blank_answer_word_id"],
    "blank_options_word_ids": ["blank_options_word_ids"],
    "grammar_point": ["grammar_point", "ng\u1eef ph\u00e1p", "ngu phap"],
    "grammar_ids": ["grammar_ids"],
    "max_word_lesson_order": ["max_word_lesson_order", "max word lesson", "t\u1eeb t\u1ed1i \u0111a b\u00e0i"],
    "validation_status": ["validation_status"],
    "scope_rule": ["scope_rule"],
    "note": ["note", "ghi ch\u00fa", "ghi chu"],
}

LESSON_COLUMNS = {
    "id": ["lesson_id", "id", "bai_id"],
    "name": ["lesson_name", "name", "t\u00ean b\u00e0i", "ten bai"],
    "order_index": ["order_index", "lesson_order", "s\u1ed1 b\u00e0i", "so bai"],
    "level": ["level", "hsk"],
    "description": ["description", "m\u00f4 t\u1ea3", "mo ta"],
    "is_active": ["is_active", "active"],
}

TOPIC_COLUMNS = {
    "id": ["topic_id", "id"],
    "name": ["topic_name", "name", "ch\u1ee7 \u0111\u1ec1", "chu de"],
    "description": ["description", "m\u00f4 t\u1ea3", "mo ta"],
    "is_active": ["is_active", "active"],
}

GRAMMAR_COLUMNS = {
    "id": ["grammar_id", "id"],
    "title_vi": ["title_vi", "title", "\u0111i\u1ec3m ng\u1eef ph\u00e1p", "diem ngu phap"],
    "pattern": ["pattern", "c\u00f4ng th\u1ee9c / c\u1ea5u tr\u00fac", "cong thuc / cau truc"],
    "explanation_vi": ["explanation_vi", "gi\u1ea3i th\u00edch", "giai thich"],
    "example_hanzi": ["example_hanzi", "v\u00ed d\u1ee5 ti\u1ebfng trung", "vi du tieng trung"],
    "example_pinyin": ["example_pinyin"],
    "example_vi": ["example_vi", "ngh\u0129a ti\u1ebfng vi\u1ec7t", "nghia tieng viet"],
    "level": ["level", "hsk"],
    "lesson_id": ["lesson_id", "b\u00e0i", "bai"],
    "lesson_order": ["lesson_order", "s\u1ed1 b\u00e0i", "so bai"],
    "tags": ["tags"],
    "is_active": ["is_active", "active"],
}

RADICAL_COLUMNS = {
    "id": ["radical_id", "id"],
    "radical": ["b\u1ed9 th\u1ee7", "bo thu", "radical"],
    "hanzi_in_words": ["h\u00e1n t\u1ef1 trong c\u1ed9t b", "han tu trong cot b"],
    "pinyin": ["pinyin"],
    "han_viet": ["h\u00e1n vi\u1ec7t", "han viet"],
    "meaning_vi": ["ngh\u0129a vi\u1ec7t nam", "nghia viet nam", "ngh\u0129a", "nghia"],
    "memory_tip": ["c\u00e1ch nh\u1edb", "cach nho"],
    "semantic_note": ["\u00fd ngh\u0129a b\u1ed9", "y nghia bo"],
    "common_words": ["t\u1eeb v\u1ef1ng th\u01b0\u1eddng xu\u1ea5t hi\u1ec7n theo b\u1ed9 th\u1ee7", "tu vung thuong xuat hien theo bo thu"],
    "is_active": ["is_active", "active"],
}


def pick(row: dict[str, str], names: list[str], default: str = "") -> str:
    normalized = {key.strip().lower(): value for key, value in row.items()}
    for name in names:
        value = normalized.get(name.lower())
        if value:
            return value
    return default

