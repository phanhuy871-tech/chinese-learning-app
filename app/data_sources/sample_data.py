from app.learning.schemas import GrammarPoint, Lesson, Topic
from app.radicals.schemas import Radical
from app.sentences.schemas import Sentence
from app.vocabulary.schemas import Word


SAMPLE_LESSONS = [
    Lesson(id="lesson-1", name="Bai 1", order_index=1, level="HSK1"),
    Lesson(id="lesson-2", name="Bai 2", order_index=2, level="HSK1"),
    Lesson(id="lesson-3", name="Bai 3", order_index=3, level="HSK1"),
]

SAMPLE_TOPICS = [
    Topic(id="greeting", name="Chao hoi"),
    Topic(id="school", name="Truong hoc"),
    Topic(id="language", name="Ngon ngu"),
]

SAMPLE_GRAMMAR_POINTS = [
    GrammarPoint(
        id="grammar-like",
        title_vi="Cau truc thich lam gi",
        pattern="S + xihuan + V/O",
        explanation_vi="Dung de noi ai do thich mot hanh dong hoac su vat.",
        example_hanzi="\u6211\u559c\u6b22\u5b66\u4e60\u4e2d\u6587",
        example_pinyin="wo xi huan xue xi zhong wen",
        example_vi="Toi thich hoc tieng Trung",
        lesson_id="lesson-2",
        lesson_order=2,
    )
]

SAMPLE_RADICALS = [
    Radical(
        id="radical-person",
        radical="\u4eba",
        variants=["\u4eba", "\u4ebb"],
        pinyin="ren",
        han_viet="Nhan",
        meaning_vi="nguoi",
        memory_tip="Dang nguoi dung thang; khi dung ben trai thuong viet la \u4ebb.",
        semantic_note="Lien quan den con nguoi, than phan, hanh dong cua nguoi.",
        common_words=["\u4f60", "\u4ed6"],
    ),
    Radical(
        id="radical-mouth",
        radical="\u53e3",
        variants=["\u53e3"],
        pinyin="kou",
        han_viet="Khau",
        meaning_vi="mieng",
        memory_tip="Hinh cai mieng vuong.",
        semantic_note="Lien quan den noi, hoi, an uong, am thanh.",
        common_words=["\u53e3", "\u5417", "\u8bed"],
    ),
]

SAMPLE_WORDS = [
    Word(id="w1", hanzi="\u4f60\u597d", pinyin="ni hao", pinyin_no_tone="ni hao", meaning_vi="xin chao", level="HSK1", lesson_id="lesson-1", lesson_order=1, topic_id="greeting", decomposition="Bo nhan dung + bo khau"),
    Word(id="w2", hanzi="\u8c22\u8c22", pinyin="xie xie", pinyin_no_tone="xie xie", meaning_vi="cam on", level="HSK1", lesson_id="lesson-1", lesson_order=1, topic_id="greeting"),
    Word(id="w3", hanzi="\u518d\u89c1", pinyin="zai jian", pinyin_no_tone="zai jian", meaning_vi="tam biet", level="HSK1", lesson_id="lesson-1", lesson_order=1, topic_id="greeting"),
    Word(id="w4", hanzi="\u8001\u5e08", pinyin="lao shi", pinyin_no_tone="lao shi", meaning_vi="giao vien", level="HSK1", lesson_id="lesson-2", lesson_order=2, topic_id="school"),
    Word(id="w5", hanzi="\u5b66\u751f", pinyin="xue sheng", pinyin_no_tone="xue sheng", meaning_vi="hoc sinh", level="HSK1", lesson_id="lesson-2", lesson_order=2, topic_id="school"),
    Word(id="w6", hanzi="\u4e2d\u6587", pinyin="zhong wen", pinyin_no_tone="zhong wen", meaning_vi="tieng Trung", level="HSK1", lesson_id="lesson-2", lesson_order=2, topic_id="language"),
    Word(id="w7", hanzi="\u559c\u6b22", pinyin="xi huan", pinyin_no_tone="xi huan", meaning_vi="thich", level="HSK1", lesson_id="lesson-2", lesson_order=2, topic_id="language", word_type="verb"),
    Word(id="w8", hanzi="\u5b66\u4e60", pinyin="xue xi", pinyin_no_tone="xue xi", meaning_vi="hoc tap", level="HSK1", lesson_id="lesson-2", lesson_order=2, topic_id="school", word_type="verb"),
    Word(id="w9", hanzi="\u4eca\u5929", pinyin="jin tian", pinyin_no_tone="jin tian", meaning_vi="hom nay", level="HSK1", lesson_id="lesson-3", lesson_order=3, topic_id="time"),
]

SAMPLE_SENTENCES = [
    Sentence(
        id="s1",
        target_word_id="w6",
        target_hanzi="\u4e2d\u6587",
        sentence_slot=1,
        sentence_hanzi="\u6211\u559c\u6b22\u5b66\u4e60\u4e2d\u6587",
        sentence_pinyin="wo xi huan xue xi zhong wen",
        sentence_vi="Toi thich hoc tieng Trung",
        words=["\u6211", "\u559c\u6b22", "\u5b66\u4e60", "\u4e2d\u6587"],
        word_ids=["w7", "w8", "w6"],
        blank_sentence="\u6211\u559c\u6b22\u5b66\u4e60___",
        blank_answer_hanzi="\u4e2d\u6587",
        blank_answer_word_id="w6",
        blank_options_word_ids=["w4", "w5", "w6"],
        grammar_ids=["grammar-like"],
        level="HSK1",
        lesson_id="lesson-2",
        lesson_order=2,
        max_word_lesson_order=2,
        topic_id="language",
    )
]
