import unittest

from app.data_sources.local_snapshot import load_local_snapshot
from app.database.repository import repository
from app.games.common.option_generator import build_word_options
from app.games.common.similarity import pinyin_similarity_score
from app.games.registry import build_game_question, list_game_types
from app.vocabulary.schemas import Word


class GameModuleTest(unittest.TestCase):
    def setUp(self) -> None:
        loaded = load_local_snapshot()
        self.assertIsNotNone(loaded)

    def test_word_games_build_valid_options(self) -> None:
        word_games = [
            "audio_to_hanzi",
            "audio_to_pinyin",
            "audio_to_meaning",
            "hanzi_to_pinyin",
            "hanzi_to_meaning",
            "pinyin_to_hanzi",
            "pinyin_to_meaning",
        ]
        for game_type in word_games:
            with self.subTest(game_type=game_type):
                question = build_game_question(game_type, lesson_order=1, item_index=0)
                option_ids = {option.id for option in question.options}
                self.assertIn(question.answer_id, option_ids)
                self.assertGreaterEqual(len(question.options), 2)

    def test_sentence_blank_builds_question(self) -> None:
        question = build_game_question("sentence_blank", lesson_order=1, item_index=0)
        option_ids = {option.id for option in question.options}

        self.assertEqual(question.game_type, "sentence_blank")
        self.assertIn(question.answer_id, option_ids)
        self.assertTrue(question.question_text)

    def test_sentence_ordering_includes_vietnamese_translation(self) -> None:
        question = build_game_question("sentence_ordering", lesson_order=1, item_index=0)

        self.assertEqual(question.game_type, "sentence_ordering")
        self.assertTrue(question.explanation["sentence_hanzi"])
        self.assertTrue(question.explanation["sentence_pinyin"])
        self.assertTrue(question.explanation["sentence_vi"])

    def test_audio_choice_has_speak_fallback(self) -> None:
        question = build_game_question("hanzi_to_audio", lesson_order=1, item_index=0)

        self.assertTrue(all(option.value for option in question.options))
        self.assertIn(question.answer_id, {option.id for option in question.options})

    def test_game_registry_lists_expected_games(self) -> None:
        game_types = list_game_types()

        self.assertIn("hanzi_to_pinyin", game_types)
        self.assertIn("sentence_blank", game_types)

    def test_selected_lesson_targets_exact_lesson_word(self) -> None:
        question = build_game_question("hanzi_to_pinyin", lesson_order=6, item_index=0)

        self.assertEqual(question.explanation["lesson_id"], "lesson-6")

    def test_two_character_word_gets_two_character_distractors(self) -> None:
        question = build_game_question("hanzi_to_pinyin", lesson_order=6, item_index=0)
        distractors = [option for option in question.options if option.id != question.answer_id]
        words_by_id = {word.id: word for word in repository.list_words()}
        two_character_count = sum(1 for option in distractors if len(words_by_id[option.id].hanzi) == 2)

        self.assertGreaterEqual(two_character_count, 2)

    def test_pinyin_similarity_prefers_tone_only_difference(self) -> None:
        tone_only = pinyin_similarity_score("mǎi", "mài")
        one_sound_change = pinyin_similarity_score("mǎi", "měi")
        unrelated = pinyin_similarity_score("mǎi", "hǎo")

        self.assertGreater(tone_only, one_sound_change)
        self.assertGreater(one_sound_change, unrelated)

    def test_pinyin_options_are_unique_and_include_tone_neighbor(self) -> None:
        correct = Word(
            id="correct",
            hanzi="买",
            pinyin="mǎi",
            pinyin_no_tone="mai",
            meaning_vi="mua",
            lesson_order=1,
        )
        candidates = [
            correct,
            Word(id="tone", hanzi="卖", pinyin="mài", pinyin_no_tone="mai", meaning_vi="bán", lesson_order=1),
            Word(id="near", hanzi="美", pinyin="měi", pinyin_no_tone="mei", meaning_vi="đẹp", lesson_order=1),
            Word(id="near-2", hanzi="慢", pinyin="màn", pinyin_no_tone="man", meaning_vi="chậm", lesson_order=1),
            Word(id="far", hanzi="好", pinyin="hǎo", pinyin_no_tone="hao", meaning_vi="tốt", lesson_order=1),
            Word(id="duplicate", hanzi="另", pinyin="mǎi", pinyin_no_tone="mai", meaning_vi="khác", lesson_order=1),
        ]

        options = build_word_options(
            correct=correct,
            candidates=candidates,
            mode="pinyin",
            strategy="similar_pinyin",
        )
        option_texts = [option.text for option in options]
        option_ids = {option.id for option in options}

        self.assertEqual(len(option_texts), len(set(option_texts)))
        self.assertIn("tone", option_ids)
        self.assertNotIn("duplicate", option_ids)

    def test_lesson_six_sentence_translation_is_repaired(self) -> None:
        question = build_game_question("sentence_blank", lesson_order=6, item_index=0)

        self.assertEqual(question.explanation["sentence_hanzi"], "请问，您贵姓？")
        self.assertEqual(question.explanation["sentence_vi"], "Xin hỏi, ngài họ gì?")


if __name__ == "__main__":
    unittest.main()
