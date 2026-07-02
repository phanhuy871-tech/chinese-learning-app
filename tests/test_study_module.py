import unittest

from app.data_sources.bootstrap import load_sample_data
from app.database.repository import repository
from app.radicals.schemas import Radical
from app.vocabulary.schemas import Word
from app.vocabulary.study_service import build_study_card, radicals_for_word, sentences_for_word


class StudyModuleTest(unittest.TestCase):
    def setUp(self) -> None:
        load_sample_data()

    def test_radicals_match_from_decomposition(self) -> None:
        word = Word(
            id="test-word",
            hanzi="\u4f60\u597d",
            pinyin="ni hao",
            meaning_vi="xin chao",
            decomposition="\u4ebb + \u53e3",
        )
        radicals = [
            Radical(id="person", radical="\u4eba", variants=["\u4eba", "\u4ebb"]),
            Radical(id="mouth", radical="\u53e3", variants=["\u53e3"]),
        ]

        matches = radicals_for_word(word, radicals)

        self.assertEqual([radical.id for radical in matches], ["person", "mouth"])

    def test_sentences_match_target_word(self) -> None:
        word = repository.get_word("w6")
        self.assertIsNotNone(word)

        matches = sentences_for_word(word, repository.list_sentences())

        self.assertGreaterEqual(len(matches), 1)
        self.assertEqual(matches[0].target_word_id, "w6")

    def test_build_study_card_shape(self) -> None:
        word = repository.get_word("w1")
        self.assertIsNotNone(word)

        card = build_study_card(word, repository.list_radicals(), repository.list_sentences())

        self.assertIn("word", card)
        self.assertIn("radicals", card)
        self.assertIn("sentences", card)
        self.assertEqual(card["word"].id, "w1")
        self.assertGreaterEqual(len(card["radicals"]), 1)

    def test_lesson_filter_has_only_exact_lesson_words(self) -> None:
        lesson_words = [word for word in repository.list_words() if word.lesson_order == 1]

        self.assertTrue(lesson_words)
        self.assertTrue(all(word.lesson_order == 1 for word in lesson_words))


if __name__ == "__main__":
    unittest.main()

