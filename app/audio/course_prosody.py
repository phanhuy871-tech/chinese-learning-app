"""Reviewed listening rhythm; punctuation is audio-only, source text is untouched."""
import re

COURSE_RATE = '-22%'
READINGS = [
    '我要去北京旅游。你觉得，什么时候去最好？',
    '九月，去北京旅游最好。',
    '为什么？',
    '九月的北京，天气不冷不热。',
    '你喜欢什么运动？',
    '我最喜欢踢足球。',
    '下午，我们一起去踢足球吧。',
    '好啊。',
    '我们要不要，买几个新的椅子？',
    '什么时候去买？',
    '明天下午，怎么样？',
    '你明天，几点能回来？',
    '三点多。',
    '桌子下面，有个猫。',
    '那是我的猫，他叫花花。',
    '她很漂亮。',
    '是啊，我觉得，她的眼睛最漂亮。',
    '他多大了？',
    '六个多月。',
]


def characters(text):
    return re.sub(r'[^\u3400-\u9fff]', '', text)


_READINGS = {characters(text): text for text in READINGS}


def course_speech_text(text):
    # Unknown sentences retain their original punctuation. Never infer pauses
    # from arbitrary line wrapping, which may fall in the middle of a phrase.
    return _READINGS.get(characters(text), text) if not re.search(r'[A-Za-z0-9]', text) else text
