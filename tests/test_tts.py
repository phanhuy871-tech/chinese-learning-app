import unittest
from app.audio.tts_service import clean_tts_text, MAX_TEXT_LENGTH


class TtsTextTest(unittest.TestCase):
    def test_long_text_is_not_silently_cut(self):
        text = '我' * 181 + '个'
        self.assertEqual(clean_tts_text(text), text)

    def test_over_limit_is_explicit_error(self):
        with self.assertRaises(ValueError):
            clean_tts_text('我' * (MAX_TEXT_LENGTH + 1))

    def test_normalization_preserves_letters_and_punctuation(self):
        self.assertEqual(clean_tts_text(' 买几个\n新的椅子？ '), '买几个 新的椅子？')
