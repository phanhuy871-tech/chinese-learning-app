from pydantic import BaseModel, Field


class Lesson(BaseModel):
    """Một bài/nhóm học, ví dụ Nhóm 1, Nhóm 2."""

    id: str
    name: str
    order_index: int
    level: str = ""
    description: str = ""
    is_active: bool = True


class Topic(BaseModel):
    """Chủ đề phân loại từ vựng, chuẩn bị cho bộ lọc sau này."""

    id: str
    name: str
    description: str = ""
    is_active: bool = True


class GrammarPoint(BaseModel):
    """Một điểm ngữ pháp trong tab ngữ pháp."""

    id: str
    title_vi: str
    pattern: str = ""
    explanation_vi: str = ""
    example_hanzi: str = ""
    example_pinyin: str = ""
    example_vi: str = ""
    level: str = ""
    lesson_id: str = ""
    lesson_order: int = 0
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True
