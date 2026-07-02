from pydantic import BaseModel, Field


class Word(BaseModel):
    """Một dòng từ vựng sau khi đọc từ Google Sheet.

    Đây là dữ liệu gốc cho module học từ vựng và hầu hết game từ vựng.
    """

    id: str
    hanzi: str
    pinyin: str
    pinyin_no_tone: str = ""
    meaning_vi: str
    meaning_en: str = ""
    word_type: str = ""
    level: str = ""
    lesson_id: str = ""
    lesson_order: int = 0
    topic_id: str = ""
    grammar_ids: list[str] = Field(default_factory=list)
    audio_url: str = ""
    image_url: str = ""
    decomposition: str = ""
    example_sentence_hanzi: str = ""
    example_sentence_pinyin: str = ""
    example_sentence_vi: str = ""
    difficulty: int = Field(default=1, ge=1, le=5)
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True
