"""Reviewed teaching overlays apply identically to Sheet and snapshot records."""
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data" / "local"
REFERENCE_CHARS = set("丌乂乜亥卅壬夬巳廿弋弗彖戈戊戋毋氐爿甪矢禺缶耒聿臾艮芈豕豸酉")
HAN_VIET = {"里": "lý", "又": "hựu", "更": "canh / cánh", "年": "niên", "女": "nữ", "水": "thủy", "儿": "nhi", "二": "nhị", "子": "tử", "主": "chủ", "未": "vị", "尸": "thi", "东": "đông", "丹": "đan", "百": "bách"}

# Reading-specific definitions: do not attach all senses to all pronunciations.
READINGS = {
    "了": [("le", "trợ từ hoàn tất hoặc thay đổi tình huống; không phải dấu quá khứ dùng cho mọi câu", "我吃饭了"), ("liǎo", "hiểu rõ trong 了解; xong/được trong 不了、得了", "了解")],
    "几": [("jǐ", "mấy, vài", "几个"), ("jī", "gần như trong 几乎; bàn nhỏ trong 茶几", "几乎")],
    "干": [("gān", "khô; can dự", "干燥"), ("gàn", "làm; thân/cán trong 树干", "干活")],
    "长": [("cháng", "dài, lâu", "很长"), ("zhǎng", "lớn lên; người đứng đầu", "长大")],
    "重": [("zhòng", "nặng; quan trọng", "重要"), ("chóng", "lại, lặp lại; tầng/lớp", "重新")],
    "为": [("wèi", "vì, cho, vì lợi ích của", "为你"), ("wéi", "làm, là, trở thành trong 成为", "成为")],
    "乐": [("lè", "vui vẻ", "快乐"), ("yuè", "âm nhạc", "音乐")],
    "少": [("shǎo", "ít, thiếu", "很少"), ("shào", "trẻ, thiếu niên", "少年")],
    "中": [("zhōng", "giữa, trong; Trung Quốc", "中间"), ("zhòng", "trúng, đạt", "中奖")],
    "斗": [("dǒu", "đấu, dụng cụ đong; hình cái gáo", "北斗"), ("dòu", "đấu, đánh nhau", "战斗")],
    "正": [("zhèng", "đúng, chính; đang", "正确"), ("zhēng", "tháng Giêng âm lịch", "正月")],
    "曲": [("qǔ", "khúc nhạc, bài hát", "歌曲"), ("qū", "cong, quanh co", "弯曲")],
    "更": [("gèng", "hơn, càng", "更好"), ("gēng", "đổi, thay; canh giờ cổ", "更换")],
    "系": [("xì", "hệ/khoa; quan hệ", "关系"), ("jì", "buộc, thắt", "系好")],
    "爪": [("zhǎo", "móng vuốt, thường trong từ ghép", "爪牙"), ("zhuǎ", "chân/vuốt động vật, khẩu ngữ", "爪子")],
    "血": [("xuè", "máu; thường dùng trong từ ghép/văn viết", "血液"), ("xiě", "máu, cách đọc khẩu ngữ", "流血")],
}


@lru_cache(maxsize=1)
def teaching_data():
    meanings = {}
    for line in (ROOT / "monolithic_meanings.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        char, pinyin, meaning = line.split("|", 2)
        meanings[char] = {"pinyin": pinyin, "senses": [s.strip() for s in meaning.split(";")]}
    examples = []
    for line in (ROOT / "monolithic_examples.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        hanzi, pinyin, meaning, links = line.split("|", 3)
        glossary = [part.split(":", 1) for part in links.split(";")]
        examples.append((hanzi, pinyin, meaning, glossary))
    return meanings, examples


def enrich_character(item):
    meanings, examples = teaching_data()
    info = meanings.get(item.simplified)
    if not info:
        return item
    char = item.simplified
    matched = []
    for hanzi, pinyin, meaning, glossary in examples:
        links = [(word, gloss) for word, gloss in glossary if char in word]
        if not links:
            continue
        focus, gloss = links[0]
        matched.append({"hanzi": hanzi, "pinyin": pinyin, "meaning_vi": meaning,
                        "focus": focus, "explanation_vi": f"{focus} → {gloss}.", "kind": "reference" if char in REFERENCE_CHARS else "daily"})
    # Prefer short sentences while keeping independently authored examples.
    matched.sort(key=lambda example: (any(c in REFERENCE_CHARS for c in example["hanzi"]), len(example["hanzi"])))
    readings = READINGS.get(char, [(info["pinyin"], "; ".join(info["senses"]), char)])
    return item.model_copy(update={
        "pinyin": info["pinyin"], "meaning_vi": "; ".join(info["senses"]),
        "han_viet": HAN_VIET.get(char, item.han_viet),
        "origin_meaning_vi": info["senses"][0], "derived_meaning_vi": "; ".join(info["senses"][1:]),
        "meanings": info["senses"],
        "readings": [{"pinyin": py, "meaning_vi": meaning, "audio_text": audio} for py, meaning, audio in readings],
        "examples": matched[:3],
        "usage_note_vi": ("Chữ ít gặp trong giao tiếp: ví dụ dưới đây giúp nhận diện chữ trong văn viết, tên riêng hoặc bài học chữ." if char in REFERENCE_CHARS else "Từ tô màu cho biết chữ đang nằm trong từ nào và cả từ ấy có nghĩa gì. Không dịch từ ghép bằng cách cộng máy móc nghĩa từng chữ."),
    })
