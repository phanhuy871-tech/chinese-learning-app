from pydantic import BaseModel, Field


class Radical(BaseModel):
    """Một bộ thủ trong tab bộ thủ.

    Dữ liệu này được dùng ở module học bộ thủ và phần chiết tự của từ vựng.
    """

    id: str
    radical: str
    variants: list[str] = Field(default_factory=list)
    pinyin: str = ""
    han_viet: str = ""
    meaning_vi: str = ""
    memory_tip: str = ""
    semantic_note: str = ""
    common_words: list[str] = Field(default_factory=list)
    is_active: bool = True
