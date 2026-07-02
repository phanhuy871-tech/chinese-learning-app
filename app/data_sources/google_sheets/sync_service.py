from app.core.config import settings
from app.data_sources.google_sheets.client import fetch_public_sheet_rows, fetch_public_sheet_rows_by_name
from app.data_sources.google_sheets.parser import (
    parse_grammar_points,
    parse_lessons,
    parse_radicals,
    parse_sentences,
    parse_topics,
    parse_words,
)
from app.database.repository import repository
from app.data_sources.local_snapshot import supplement_lessons_from_words


def sync_google_sheet() -> dict[str, int]:
    words_rows = fetch_public_sheet_rows_by_name(settings.google_sheet_id, settings.google_words_sheet)
    sentences_rows = fetch_public_sheet_rows_by_name(settings.google_sheet_id, settings.google_sentences_sheet)
    grammar_rows = fetch_public_sheet_rows_by_name(settings.google_sheet_id, settings.google_grammar_sheet)
    radical_rows = fetch_public_sheet_rows_by_name(settings.google_sheet_id, settings.google_radicals_sheet)

    try:
        lessons_rows = fetch_public_sheet_rows_by_name(settings.google_sheet_id, settings.google_lessons_sheet)
    except Exception:
        lessons_rows = words_rows

    try:
        topics_rows = fetch_public_sheet_rows_by_name(settings.google_sheet_id, settings.google_topics_sheet)
    except Exception:
        topics_rows = words_rows

    words = parse_words(words_rows)
    sentences = parse_sentences(sentences_rows)
    lessons = parse_lessons(lessons_rows)
    topics = parse_topics(topics_rows)
    grammar_points = parse_grammar_points(grammar_rows)
    radicals = parse_radicals(radical_rows)
    lessons = supplement_lessons_from_words(lessons, words)
    repository.replace_words(words)
    repository.replace_sentences(sentences)
    repository.replace_lessons(lessons)
    repository.replace_topics(topics)
    repository.replace_grammar_points(grammar_points)
    repository.replace_radicals(radicals)
    return {
        "word_rows": len(words_rows),
        "sentence_rows": len(sentences_rows),
        "grammar_rows": len(grammar_rows),
        "radical_rows": len(radical_rows),
        "words": len(words),
        "sentences": len(sentences),
        "lessons": len(lessons),
        "topics": len(topics),
        "grammar_points": len(grammar_points),
        "radicals": len(radicals),
    }
