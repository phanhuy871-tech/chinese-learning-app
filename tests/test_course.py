import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from app.learning import course
from app.learning.course import parse_course, media_url, SNAPSHOT

class CourseTest(unittest.TestCase):
    def test_speech_rhythm_preserves_source_characters(self):
        from app.audio.course_prosody import course_speech_text, course_speech_segments, characters, COURSE_RATE
        self.assertEqual(COURSE_RATE, '-22%')
        for row in json.loads(SNAPSHOT.read_text(encoding='utf-8')):
            self.assertEqual(characters(course_speech_text(row['hanzi'])), characters(row['hanzi']))
            self.assertEqual(characters(''.join(course_speech_segments(row['hanzi']))), characters(row['hanzi']))
        self.assertEqual(course_speech_text('九月去北京旅游最好'), '九月，去北京旅游，最好。')
        self.assertEqual(course_speech_text('我们要不要买几个新的椅子？'), '我们要不要，买几个，新的椅子？')
        self.assertEqual(course_speech_text('未知的句子'), '未知的句子')

    def test_token_hints(self):
        from app.learning.course_tokens import token_hints
        hints = token_hints('九月去北京旅游最好', 'jiǔ yuè qù běi jīng lǚ yóu zuì hǎo')
        self.assertEqual(hints[2], {'character_count': 2, 'pinyin_initials': 'B J'})
        self.assertEqual(hints[3]['pinyin_initials'], 'L Y')
        self.assertTrue(all(not h['pinyin_initials'] for h in token_hints('为什么', 'wèishénme')))
        for lesson in parse_course(json.loads(SNAPSHOT.read_text(encoding='utf-8'))):
            for sentence in lesson['sentences']:
                hints = sentence['listening_token_hints']
                self.assertEqual(len(hints), len(sentence['listening_tokens']))
                self.assertTrue(all(h['pinyin_initials'] for h in hints))

    def test_refresh_persists_and_survives_cache_reset(self):
        rows = [{'lesson_id':'BK01','sentence_id':'C1','hanzi':'我','sentence_order':1}]
        with tempfile.TemporaryDirectory() as directory, patch.object(course, 'STORE', Path(directory)/'course.json'), patch.object(course, '_cached', None), patch.object(course, 'fetch_public_sheet_rows_by_name', return_value=rows):
            expected = course.refresh_course()
            course._cached = None
            self.assertEqual(course.course_lessons(), expected)
            before = course.STORE.read_bytes()
            with patch.object(course, 'fetch_public_sheet_rows_by_name', return_value=[]):
                with self.assertRaises(course.HTTPException): course.refresh_course()
            self.assertEqual(course.STORE.read_bytes(), before)
            with patch.object(course, 'persist_rows', side_effect=OSError('disk full')):
                with self.assertRaises(course.HTTPException): course.refresh_course()
            self.assertEqual(course.course_lessons(), expected)

    def test_approved_correction_is_narrow_and_preserves_source(self):
        source = {'sentence_id':'BK04-C02','hanzi':'那是我的毛，他叫花花'}
        fixed = course.corrected_rows([source])[0]
        self.assertEqual(fixed['hanzi'], '那是我的猫，他叫花花')
        self.assertEqual(fixed['source_hanzi'], source['hanzi'])
        self.assertEqual(source['hanzi'], '那是我的毛，他叫花花')
        self.assertIn('māo', fixed['pinyin'])
        self.assertEqual(course.corrected_rows([fixed]), [fixed])
        other = {**source,'sentence_id':'OTHER'}
        self.assertEqual(course.corrected_rows([other]), [other])

    def test_snapshot(self):
        rows = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
        lessons = parse_course(rows)
        self.assertEqual([len(l['sentences']) for l in lessons], [4,4,6,6])
        self.assertEqual(lessons[0]['sentences'][0]['hanzi'], rows[0]['hanzi'])
        self.assertTrue(lessons[0]['sentences'][0]['image_url'].endswith('BK01.jpg'))

    def test_invalid_and_duplicates(self):
        row = {'lesson_id':'BK01','sentence_id':'C1','hanzi':'我','sentence_order':1}
        with self.assertRaises(ValueError): parse_course([row,row])
        with self.assertRaises(ValueError): parse_course([{}])
        with self.assertRaises(ValueError): parse_course([row,{**row,'sentence_id':'C2'}])

    def test_media(self):
        self.assertEqual(media_url('javascript:alert(1)'), '')
        self.assertEqual(media_url('../secret'), '')
        self.assertEqual(media_url('C:\\image.png'), '')
        self.assertEqual(media_url('BK01.jpg'), '/static/course-images/BK01.jpg')

    def test_revision(self):
        row={'lesson_id':'BK01','sentence_id':'C1','hanzi':'我','sentence_order':1}
        self.assertNotEqual(parse_course([row])[0]['revision'],parse_course([{**row,'hanzi':'你'}])[0]['revision'])

    def test_generated_audio_matches_text_and_speaker(self):
        rows = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
        lessons = parse_course(rows)
        all_sentences = [s for l in lessons for s in l['sentences']]
        self.assertTrue(all(s['audio_url'].startswith('/static/course-audio/') for s in all_sentences))
        changed = {**rows[0], 'hanzi': '你好'}
        self.assertEqual(parse_course([changed])[0]['sentences'][0]['audio_url'], '')
        changed = {**rows[0], 'speaker': 'B'}
        self.assertEqual(parse_course([changed])[0]['sentences'][0]['audio_url'], '')

    def test_han_viet_is_separate_from_meaning(self):
        rows = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
        s = parse_course(rows)[0]['sentences'][0]
        word = next(w for w in s['word_glossary'] if w['hanzi']=='旅游')
        self.assertEqual(word['han_viet'], 'lữ du')
        self.assertEqual(word['meaning_vi'], 'Đi du lịch.')

    def test_listening_tokens_cover_source_without_changing_it(self):
        import re
        rows = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
        for lesson in parse_course(rows):
            for s in lesson['sentences']:
                self.assertTrue(s['listening_tokens'])
                self.assertEqual(''.join(s['listening_tokens']), re.sub(r'[^\u3400-\u9fff]', '', s['hanzi']))
        from app.learning.course_tokens import listening_tokens
        self.assertEqual(listening_tokens('新的未知句子'), [])
