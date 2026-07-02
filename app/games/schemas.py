from pydantic import BaseModel, Field


class GameOption(BaseModel):
    """Một lựa chọn trả lời trong game."""

    id: str
    text: str = ""
    audio_url: str = ""
    value: str = ""


class GameQuestion(BaseModel):
    """Format chung của mọi câu hỏi game gửi từ backend sang frontend.

    Nhờ dùng format chung, JavaScript chỉ cần một hàm render chính cho nhiều loại game.
    """

    game_type: str
    prompt: str
    lesson_order: int
    question_text: str = ""
    hanzi: str = ""
    pinyin: str = ""
    meaning_vi: str = ""
    audio_url: str = ""
    options: list[GameOption] = Field(default_factory=list)
    answer_id: str
    explanation: dict[str, str] = Field(default_factory=dict)
