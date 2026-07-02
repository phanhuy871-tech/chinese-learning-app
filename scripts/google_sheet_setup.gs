function setupChineseLearningSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const tabs = {
    lessons: [
      "lesson_id",
      "lesson_order",
      "lesson_name",
      "level",
      "description",
      "is_active",
    ],
    topics: [
      "topic_id",
      "topic_name",
      "description",
      "is_active",
    ],
    grammar: [
      "grammar_id",
      "title_vi",
      "pattern",
      "explanation_vi",
      "example_hanzi",
      "example_pinyin",
      "example_vi",
      "level",
      "lesson_id",
      "lesson_order",
      "tags",
      "is_active",
    ],
    words: [
      "word_id",
      "hanzi",
      "pinyin",
      "pinyin_no_tone",
      "meaning_vi",
      "meaning_en",
      "word_type",
      "level",
      "lesson_id",
      "lesson_order",
      "topic_id",
      "grammar_ids",
      "audio_url",
      "image_url",
      "difficulty",
      "tags",
      "is_active",
    ],
    sentences: [
      "sentence_id",
      "sentence_hanzi",
      "sentence_pinyin",
      "sentence_vi",
      "words",
      "word_ids",
      "blank_sentence",
      "blank_answer_hanzi",
      "blank_answer_word_id",
      "blank_options_word_ids",
      "grammar_ids",
      "level",
      "lesson_id",
      "lesson_order",
      "max_word_lesson_order",
      "topic_id",
      "audio_url",
      "difficulty",
      "tags",
      "is_active",
    ],
  };

  Object.entries(tabs).forEach(([name, headers]) => {
    let sheet = ss.getSheetByName(name);
    if (!sheet) {
      sheet = ss.insertSheet(name);
    }
    sheet.clear();
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    sheet.setFrozenRows(1);
    sheet.autoResizeColumns(1, headers.length);
  });
}

