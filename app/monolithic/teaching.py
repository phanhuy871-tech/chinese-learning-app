"""Reviewed teaching overlays apply identically to Sheet and snapshot records."""
from functools import lru_cache
from pathlib import Path
from app.monolithic.origins import origin_fields

ROOT = Path(__file__).resolve().parents[2] / "data" / "local"
REFERENCE_CHARS = set("丌乂乜亥卅壬夬巳廿弋弗彖戈戊戋毋氐爿甪矢禺缶耒聿臾艮芈豕豸酉")
HAN_VIET = {"里": "lý", "又": "hựu", "更": "canh / cánh", "年": "niên", "女": "nữ", "水": "thủy", "儿": "nhi", "二": "nhị", "子": "tử", "主": "chủ", "未": "vị", "尸": "thi", "东": "đông", "丹": "đan", "百": "bách"}
ORIGIN_STORIES = {
    "大": "Giáp cốt văn vẽ một người đứng dang rộng hai tay và hai chân. Dáng người chiếm nhiều khoảng không nên biểu thị nghĩa gốc ‘lớn, to’. Qua Kim văn và Tiểu triện, hình người được uốn thành nét; Khải thư giữ lại chữ 大 hiện nay.",
    "人": "Giáp cốt văn là hình một người nhìn nghiêng, có đầu, thân và chân đang bước. Các nét dần thẳng hóa qua Kim văn–Tiểu triện, thành 人 trong Khải thư; nghĩa gốc vẫn là ‘người’.",
    "木": "Chữ cổ vẽ một cái cây: nét dọc là thân, nét ngang là cành, hai nét xòe xuống là rễ. Tiểu triện làm hình cân đối hơn, Khải thư rút gọn thành 木; nghĩa gốc là ‘cây, gỗ’.",
    "日": "Giáp cốt văn vẽ mặt trời như một vòng tròn có dấu ở giữa để chỉ ánh sáng. Khi viết trên thẻ tre, vòng tròn thành khung vuông; qua Tiểu triện và Khải thư thành 日, nghĩa là ‘mặt trời, ngày’.",
    "月": "Chữ cổ mô phỏng mặt trăng lưỡi liềm, thường có vệt bên trong. Nét cong được chuẩn hóa thành khung dài qua Tiểu triện, rồi thành 月 trong Khải thư; nghĩa gốc là ‘trăng, tháng’.",
    "山": "Giáp cốt văn là ba đỉnh núi nhô lên. Tiểu triện nối các đỉnh bằng nét đều, Khải thư giữ ba nhánh đặc trưng của 山; nghĩa gốc là ‘núi’.",
    "水": "Chữ cổ vẽ dòng nước ở giữa và các giọt tỏa hai bên. Khi nét cong được viết thẳng, hình tiến hóa thành 水; khi làm bộ bên trái, nó co thành 氵, nghĩa gốc là ‘nước’.",
    "火": "Giáp cốt văn vẽ ngọn lửa với các tia bốc lên. Tiểu triện làm các tia thành nét đối xứng; Khải thư thành 火, nghĩa gốc là ‘lửa’. Dạng làm bộ thường viết 灬 ở dưới.",
    "土": "Hình cổ gồm một mô đất nhô lên trên mặt đất, như dấu thập có chân đế. Các nét được vuông hóa qua Tiểu triện, thành 土; nghĩa gốc là ‘đất’.",
    "口": "Giáp cốt văn vẽ thẳng miệng mở như một khung vuông. Khung được giữ gần như nguyên dạng qua các thời kỳ, thành 口; nghĩa gốc là ‘miệng, cửa mở’.",
    "目": "Chữ cổ vẽ con mắt nhìn ngang, có tròng ở giữa. Khi chữ quay dọc trên thẻ tre, hình được chuẩn hóa thành 目; nghĩa gốc là ‘mắt’ và mở rộng thành ‘mục, mục tiêu’.",
    "手": "Giáp cốt văn mô phỏng bàn tay với các ngón xòe. Nét cong dần thành hình đối xứng trong Tiểu triện rồi thành 手; khi đứng bên trái thường viết 扌.",
    "心": "Chữ cổ vẽ trái tim với các thùy và mạch máu. Tiểu triện kéo dài phần dưới, Khải thư thành 心; nghĩa gốc là ‘tim’, sau mở rộng thành lòng và tâm trí. Dạng dưới thường là 忄 hoặc ⺗.",
    "女": "Giáp cốt văn vẽ người phụ nữ quỳ, hai tay đặt trước thân. Hình được giản hóa qua Kim văn và Tiểu triện, thành 女; nghĩa gốc là ‘nữ, phụ nữ’.",
    "子": "Chữ cổ vẽ một em bé với đầu lớn, thân nhỏ và hai tay dang ra. Các nét được thẳng hóa thành 子; nghĩa gốc là ‘con, trẻ nhỏ’.",
    "田": "Giáp cốt văn vẽ thửa ruộng chia thành các ô vuông bằng bờ đất. Bố cục ô ruộng được giữ nguyên qua Tiểu triện và Khải thư, thành 田; nghĩa gốc là ‘ruộng’.",
    "天": "Chữ cổ đặt một nét ngang lớn trên hình người 大 để chỉ phần ở trên đầu. Vì vậy 天 ban đầu là ‘trời, phía trên’, rồi mở rộng thành thiên nhiên và ngày trời.",
    "上": "Chữ chỉ sự gồm một vạch chuẩn và nét nằm phía trên vạch ấy. Vị trí ‘ở trên’ được biểu thị trực tiếp, qua Tiểu triện thành 上; nghĩa gốc là ‘trên, lên’.",
    "下": "Chữ chỉ sự gồm một vạch chuẩn và nét nằm phía dưới vạch ấy. Vị trí ‘ở dưới’ được biểu thị trực tiếp, qua Tiểu triện thành 下; nghĩa gốc là ‘dưới, xuống’.",
    "中": "Giáp cốt văn vẽ một lá cờ hoặc vật thẳng đứng xuyên qua tâm một vòng/khung. Nét xuyên giữa được giữ lại, thành 中; nghĩa gốc là ‘ở giữa, trung tâm’.",
    "本": "本 được tạo từ 木 bằng một nét đánh dấu ở gốc cây. Dấu ở chân cây chỉ ‘gốc, nền tảng’; về sau mở rộng thành ‘bản, quyển, vốn’.",
    "末": "末 cũng dựa trên 木 nhưng nét đánh dấu đặt ở ngọn cây. Vì vậy nghĩa gốc là ‘ngọn, cuối’, đối lập với 本 ‘gốc’; sau mở rộng thành phần cuối.",
    "明": "明 là chữ hợp thể của 日 (mặt trời) và 月 (mặt trăng). Hai nguồn sáng cùng xuất hiện tạo ý ‘sáng, rõ’; Khải thư giữ hai thành phần trong 明.",
    "刀": "Giáp cốt văn vẽ một con dao có lưỡi và cán. Hình được viết gọn qua Kim văn–Tiểu triện thành 刀; khi đứng bên phải thường biến thành 刂.",
    "马": "Giáp cốt văn vẽ con ngựa có đầu, bờm, thân và chân. Tiểu triện làm hình đều nét; giản thể 马 rút gọn từ 馬 nhưng vẫn giữ dáng con vật.",
    "鸟": "Chữ cổ vẽ chim có mỏ, thân, cánh và chân. Các chi tiết được giản lược dần; 鸟 là dạng giản thể của 鳥, nghĩa gốc là ‘chim’.",
    "米": "Giáp cốt văn vẽ hạt lúa hoặc các hạt tỏa quanh trục. Hình đối xứng được giữ thành 米; nghĩa gốc là ‘gạo, hạt’.",
}

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
        "derived_meaning_vi": "",
        "meanings": info["senses"],
        "readings": [{"pinyin": py, "meaning_vi": meaning, "audio_text": audio} for py, meaning, audio in readings],
        "examples": matched[:3],
        "usage_note_vi": ("Chữ ít gặp trong giao tiếp: ví dụ dưới đây giúp nhận diện chữ trong văn viết, tên riêng hoặc bài học chữ." if char in REFERENCE_CHARS else "Từ tô màu cho biết chữ đang nằm trong từ nào và cả từ ấy có nghĩa gì. Không dịch từ ghép bằng cách cộng máy móc nghĩa từng chữ."),
        **origin_fields(char),
    })
