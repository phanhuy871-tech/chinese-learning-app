from app.database.repository import repository
from app.data_sources.sample_data import (
    SAMPLE_GRAMMAR_POINTS,
    SAMPLE_LESSONS,
    SAMPLE_RADICALS,
    SAMPLE_SENTENCES,
    SAMPLE_TOPICS,
    SAMPLE_WORDS,
)


def load_sample_data() -> None:
    repository.replace_lessons(SAMPLE_LESSONS)
    repository.replace_topics(SAMPLE_TOPICS)
    repository.replace_grammar_points(SAMPLE_GRAMMAR_POINTS)
    repository.replace_radicals(SAMPLE_RADICALS)
    repository.replace_words(SAMPLE_WORDS)
    repository.replace_sentences(SAMPLE_SENTENCES)
