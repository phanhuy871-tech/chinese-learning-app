"""Generate reusable Mandarin MP3s; never modify source Chinese or Sheets."""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.audio.tts_service import COURSE_VOICES, RATE, PITCH, cache_key, synthesize_chinese_audio

OUT = ROOT / 'app/web/static/course-audio'

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for row in json.loads((ROOT / 'data/local/course_lessons.json').read_text(encoding='utf-8')):
        speaker = row.get('speaker', 'A')
        voice = COURSE_VOICES.get(speaker, COURSE_VOICES['A'])
        digest = cache_key(f"{voice}|{RATE}|{PITCH}|{row['hanzi']}")
        filename = digest + '.mp3'
        path = OUT / filename
        if not path.exists():
            audio = await asyncio.wait_for(synthesize_chinese_audio(row['hanzi'], speaker), timeout=45)
            path.write_bytes(audio)
        manifest[row['sentence_id']] = {'text': row['hanzi'], 'speaker': speaker,
            'voice': voice, 'url': '/static/course-audio/' + filename, 'bytes': path.stat().st_size}
        print(row['sentence_id'], speaker, path.stat().st_size, flush=True)
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    asyncio.run(main())
