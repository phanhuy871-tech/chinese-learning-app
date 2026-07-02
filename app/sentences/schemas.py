from pydantic import BaseModel, Field


class Sentence(BaseModel):
    """Một câu ví dụ/câu game trong tab câu.

    Cùng một Sentence có thể dùng cho game sắp xếp câu và game điền từ vào chỗ trống.
    """

    id: str
    target_word_id: str = ""
    target_hanzi: str = ""
    sentence_slot: int = 1
    sentence_hanzi: str
    sentence_pinyin: str = ""
    sentence_vi: str = ""
    words: list[str] = Field(default_factory=list)
    word_ids: list[str] = Field(default_factory=list)
    blank_sentence: str = ""
    blank_answer_hanzi: str = ""
    blank_answer_word_id: str = ""
    blank_options_word_ids: list[str] = Field(default_factory=list)
    grammar_point: str = ""
    grammar_ids: list[str] = Field(default_factory=list)
    level: str = ""
    lesson_id: str = ""
    lesson_order: int = 0
    max_word_lesson_order: int = 0
    topic_id: str = ""
    audio_url: str = ""
    difficulty: int = Field(default=1, ge=1, le=5)
    is_active: bool = True
    validation_status: str = "ready"
    scope_rule: str = ""
    note: str = ""
