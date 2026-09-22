from pydantic import BaseModel, Field


class MonolithicCharacter(BaseModel):
    id: str
    simplified: str
    traditional: str = ""
    pinyin: str = ""
    han_viet: str = ""
    meaning_vi: str = ""
    origin_meaning_vi: str = ""
    derived_meaning_vi: str = ""
    etymology_type: str = ""
    etymology_note_vi: str = ""
    stroke_count: int = 0
    stroke_hint_vi: str = ""
    radical_form: str = ""
    radical_note_vi: str = ""
    week: int = 5
    category: str = "Khái niệm khác"
    core_rank: int = 0
    is_core: bool = False
    oracle_image_url: str = ""
    bronze_image_url: str = ""
    seal_image_url: str = ""
    evolution_source_url: str = ""
    compounds: list[str] = Field(default_factory=list)
    hidden_examples: list[str] = Field(default_factory=list)
    is_active: bool = True
    meanings: list[str] = Field(default_factory=list)
    readings: list[dict[str, str]] = Field(default_factory=list)
    examples: list[dict[str, str]] = Field(default_factory=list)
    usage_note_vi: str = ""
    origin_story_vi: str = ""
