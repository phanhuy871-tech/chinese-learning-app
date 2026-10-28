"""Reviewed word/phrase boundaries for the current lessons; unknown text stays free-form."""
import re
import unicodedata

PHRASES = [
    '我|要|去|北京|旅游|你|觉得|什么时候|去|最|好',
    '九月|去|北京|旅游|最|好', '为什么', '九月|的|北京|天气|不|冷|不|热',
    '你|喜欢|什么|运动', '我|最|喜欢|踢|足球', '下午|我们|一起|去|踢|足球|吧', '好|啊',
    '我们|要不要|买|几|个|新|的|椅子', '什么时候|去|买', '明天|下午|怎么样',
    '你|明天|几点|能|回来', '三点|多', '桌子|下面|有|个|猫',
    '那|是|我|的|猫|他|叫|花花', '她|很|漂亮', '是|啊|我|觉得|她|的|眼睛|最|漂亮',
    '他|多大|了', '六|个|多|月',
]
TOKEN_MAP = {p.replace('|', ''): p.split('|') for p in PHRASES}

def listening_tokens(text):
    normalized = re.sub(r'[^\u3400-\u9fff]', '', text)
    return TOKEN_MAP.get(normalized, []) if not re.search(r'[A-Za-z0-9]', text) else []


def token_hints(text, pinyin):
    """Align only explicitly separated syllables; never guess missing boundaries."""
    tokens = listening_tokens(text)
    plain = ''.join(c for c in unicodedata.normalize('NFD', pinyin.lower())
                    if not unicodedata.combining(c))
    syllables = plain.split()
    valid = (len(syllables) == sum(map(len, tokens)) and
             all(re.fullmatch(r'[a-z]+', s) for s in syllables))
    result, offset = [], 0
    for token in tokens:
        count = len(token)
        result.append({'character_count': count,
                       'pinyin_initials': ' '.join(s[0].upper() for s in syllables[offset:offset+count]) if valid else ''})
        offset += count
    return result
