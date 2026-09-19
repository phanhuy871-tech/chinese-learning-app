"""Tạo snapshot 284 chữ độc thể từ danh mục công khai và từ điển Việt-Trung.

Nguồn danh mục: glbd.net/a/zidian/dutizidaquan
Nguồn đọc/nghĩa/tần suất: xue-hanzi/CVDICT (CC BY-SA); nét: Make Me a Hanzi.
"""
from __future__ import annotations

import csv
import ast
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/local/monolithic.tsv"
SOURCE_URL = "https://www.glbd.net/a/zidian/dutizidaquan"

WEEK_GROUPS = {
    1: ("Tự nhiên & Vũ trụ", set("日月山水火土石川田云雨风气天夕光冰泉井丘谷穴沙江河海州岛辰星电雷雪冬春夏秋")),
    2: ("Con người & Cơ thể", set("人男女子儿口目耳手足心头面身尸牙舌毛血骨肉皮首眉鼻母父兄弟臣民王士鬼")),
    3: ("Động vật & Thực vật", set("牛马羊鸟鱼虫犬豕鹿象虎兔鼠龙龟贝木禾米竹瓜果豆麦麻花草苗生卵角羽爪")),
    4: ("Đồ vật & Công cụ", set("门户车刀弓矢网皿巾衣舟瓦斤斧戈矛盾弋殳册书笔伞壶鼎鼓琴床桌凳勺斗臼缶")),
}

VARIANTS = {
    "人": "亻", "水": "氵", "手": "扌", "心": "忄/⺗", "火": "灬", "犬": "犭",
    "示": "礻", "衣": "衤", "食": "饣", "金": "钅", "言": "讠", "糸": "纟",
    "刀": "刂", "牛": "牜", "足": "⻊", "攴": "攵", "玉": "王", "竹": "⺮",
    "艸": "艹", "肉": "月", "邑": "阝 (bên phải)", "阜": "阝 (bên trái)",
}

HAN_VIET_FALLBACK = {
    "乡": "hương", "幺": "yêu", "亓": "kỳ", "韦": "vi", "为": "vi/vị",
    "戋": "tiên", "电": "điện", "亚": "á", "页": "hiệt", "产": "sản",
    "芈": "mễ", "肃": "túc", "隶": "lệ",
}

FIELDS = [
    "character_id", "simplified", "traditional", "pinyin", "han_viet", "meaning_vi",
    "origin_meaning_vi", "derived_meaning_vi", "etymology_type", "etymology_note_vi",
    "stroke_count", "stroke_hint_vi", "radical_form", "radical_note_vi", "week", "category",
    "core_rank", "is_core", "oracle_image_url", "bronze_image_url", "seal_image_url",
    "evolution_source_url", "compounds", "hidden_examples", "is_active",
]


def fetch_characters() -> list[str]:
    request = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    page = urllib.request.urlopen(request, timeout=60).read().decode("utf-8")
    # Chỉ lấy liên kết một chữ trong phần bài viết, giữ thứ tự và loại bản trùng.
    candidates = re.findall(r'<a[^>]+class=han[^>]*>\s*<span>\s*([\u3400-\u9fff])\s*</span>\s*</a>', page)
    if len(set(candidates)) < 280:
        candidates = re.findall(r'<a[^>]*>\s*([\u3400-\u9fff])\s*</a>', page)
    result = []
    for char in candidates:
        if char not in result:
            result.append(char)
    if len(result) < 280:
        raise RuntimeError(f"Chỉ đọc được {len(result)} chữ từ nguồn danh mục")
    return result[:284]


def load_dictionary() -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    entries = json.loads((ROOT / ".tmp-xue-hanzi/public/data/dictionary.json").read_text(encoding="utf-8"))
    by_s = {}
    for entry in entries:
        if len(entry.get("s", "")) == 1 and entry.get("s") not in by_s:
            by_s[entry["s"]] = entry
    strokes = {}
    with (ROOT / ".tmp-makemeahanzi/dictionary.txt").open(encoding="utf-8") as handle:
        for line in handle:
            entry = json.loads(line)
            strokes[entry["character"]] = entry
    han_viet: dict[str, str] = {}
    with (ROOT / ".tmp-hanviet/hanviet.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            readings = ast.literal_eval(row["hanviet"])
            if readings and row["char"] not in han_viet:
                han_viet[row["char"]] = readings[0]
    return by_s, strokes, han_viet


def classify(char: str) -> tuple[int, str]:
    for week, (name, chars) in WEEK_GROUPS.items():
        if char in chars:
            return week, name
    return 5, "Số đếm, Phương hướng & Khái niệm"


def image_url(char: str, style: str) -> str:
    return "https://char.iis.sinica.edu.tw/TTF/getTTF1.aspx?" + urllib.parse.urlencode(
        {"word": char, "f": style, "s": "200", "c": "black"}
    )


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def build() -> list[dict[str, object]]:
    chars = fetch_characters()
    dictionary, stroke_data, han_viet = load_dictionary()
    ranked = sorted(chars, key=lambda c: (dictionary.get(c, {}).get("mwr", 999999), -dictionary.get(c, {}).get("b", 0)))
    core_rank = {char: index + 1 for index, char in enumerate(ranked[:140])}
    rows = []
    for index, char in enumerate(chars, start=1):
        entry = dictionary.get(char, {})
        stroke = stroke_data.get(char, {})
        week, category = classify(char)
        meaning_parts = [part.strip() for part in entry.get("vi", "").split(" / ") if part.strip()]
        etym = clean(entry.get("etym", {}).get("notes", ""))
        etym_type = "Tượng hình" if any(word in etym.lower() for word in ("pictograph", "picture", "depicts")) else "Chỉ sự/độc thể"
        if etym:
            note = "Đối chiếu hình chữ cổ để nhận ra nét nghĩa gốc; ghi chú nguồn: " + etym
        else:
            note = "Dạng chữ độc thể; đối chiếu Giáp Cốt văn, Kim văn và Tiểu Triện ở chuỗi hình bên cạnh."
        compounds = [item.get("word", "") for item in entry.get("tw", [])[:4] if item.get("word")]
        variant = VARIANTS.get(char, char)
        rows.append({
            "character_id": f"mono-{index:03d}", "simplified": char,
            "traditional": entry.get("t") or char, "pinyin": entry.get("p", ""),
            "han_viet": clean(entry.get("sv") or han_viet.get(char) or HAN_VIET_FALLBACK.get(char, "")), "meaning_vi": clean(entry.get("vi", "")),
            "origin_meaning_vi": meaning_parts[0] if meaning_parts else "",
            "derived_meaning_vi": " / ".join(meaning_parts[1:]), "etymology_type": etym_type,
            "etymology_note_vi": note, "stroke_count": len(stroke.get("strokes", [])),
            "stroke_hint_vi": "Viết theo hoạt ảnh từng nét trong ứng dụng; tuân thủ trên trước dưới, trái trước phải.",
            "radical_form": variant,
            "radical_note_vi": (f"Khi làm thành phần chữ ghép thường biến thành {variant}." if variant != char else "Thường giữ nguyên hình khi làm thành phần; có thể co hẹp theo vị trí."),
            "week": week, "category": category, "core_rank": core_rank.get(char, 0),
            "is_core": "TRUE" if char in core_rank else "FALSE",
            "oracle_image_url": image_url(char, "甲骨文"), "bronze_image_url": image_url(char, "金文"),
            "seal_image_url": image_url(char, "小篆"),
            "evolution_source_url": "https://chardb.iis.sinica.edu.tw/search.jsp?" + urllib.parse.urlencode({"q": char, "stype": 0}),
            "compounds": " | ".join(compounds), "hidden_examples": " | ".join(compounds[:3]), "is_active": "TRUE",
        })
    return rows


if __name__ == "__main__":
    rows = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader(); writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")
