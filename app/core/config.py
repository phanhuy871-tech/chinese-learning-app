from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Chinese Learning App"
    google_sheet_id: str = "1hM0aUWPC2ktLIWHTcqDYWmDzfAhF1hpzOgLVJPsqoAc"
    google_sheet_gid: str = "0"
    google_words_sheet: str = "t\u1eeb v\u1ef1ng"
    google_sentences_sheet: str = "c\u00e2u trong game"
    google_grammar_sheet: str = "ng\u1eef ph\u00e1p"
    google_lessons_sheet: str = "lessons"
    google_topics_sheet: str = "topics"
    google_radicals_sheet: str = "b\u1ed9 th\u1ee7"
    sync_on_startup: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

