"""Generate reusable Mandarin MP3s; never modify source Chinese or Sheets."""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.audio.tts_service import COURSE_VOICES, RATE, PITCH, cache_key, synthesize_chinese_audio
from app.audio.course_prosody import COURSE_RATE, course_speech_text, course_speech_segments

OUT = ROOT / 'app/web/static/course-audio'

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for row in json.loads((ROOT / 'data/local/course_lessons.json').read_text(encoding='utf-8')):
        speaker = row.get('speaker', 'A')
        voice = COURSE_VOICES.get(speaker, COURSE_VOICES['A'])
        speech_text = course_speech_text(row['hanzi'])
        digest = cache_key(f"course-rhythm-v1|{voice}|{COURSE_RATE}|{PITCH}|{speech_text}")
        filename = digest + '.mp3'
        path = OUT / filename
        if not path.exists():
            audio = await asyncio.wait_for(synthesize_chinese_audio(row['hanzi'], speaker), timeout=45)
            path.write_bytes(audio)
        segments = []
        for part in course_speech_segments(row['hanzi']):
            part_name = cache_key(f"course-segment-v1|{voice}|{COURSE_RATE}|{PITCH}|{part}") + '.mp3'
            part_path = OUT / part_name
            if not part_path.exists():
                part_path.write_bytes(await asyncio.wait_for(synthesize_chinese_audio(part + '。', speaker), timeout=45))
            segments.append({'text': part, 'url': '/static/course-audio/' + part_name})
        manifest[row['sentence_id']] = {'text': row['hanzi'], 'speaker': speaker,
            'segments': segments,
            'voice': voice, 'rate': COURSE_RATE, 'speech_text': speech_text,
            'url': '/static/course-audio/' + filename, 'bytes': path.stat().st_size}
        print(row['sentence_id'], speaker, path.stat().st_size, flush=True)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    asyncio.run(main())
