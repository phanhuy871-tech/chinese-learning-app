import hashlib
import os


# Xiaoxiao là giọng Quan thoại phổ thông, phát âm rõ và tự nhiên hơn cho người mới học.
# Cho phép đổi bằng biến môi trường mà không cần sửa source khi triển khai.
VOICE = os.getenv("TTS_VOICE", "zh-CN-XiaoxiaoNeural")
RATE = os.getenv("TTS_RATE", "-8%")
PITCH = os.getenv("TTS_PITCH", "+0Hz")
MAX_TEXT_LENGTH = 180
_AUDIO_CACHE: dict[str, bytes] = {}


def clean_tts_text(text: str) -> str:
    """Chuẩn hóa câu/từ cần đọc để TTS không nhận chuỗi quá dài hoặc rỗng."""
    return " ".join(str(text or "").strip().split())[:MAX_TEXT_LENGTH]


def cache_key(text: str) -> str:
    """Tạo khóa cache ngắn từ nội dung tiếng Trung cần đọc."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


async def synthesize_chinese_audio(text: str) -> bytes:
    """Tạo MP3 tiếng Trung bằng Edge neural TTS và cache trong bộ nhớ server."""
    cleaned = clean_tts_text(text)
    if not cleaned:
        raise ValueError("Không có nội dung để phát âm.")

    key = cache_key(f"{VOICE}|{RATE}|{PITCH}|{cleaned}")
    if key in _AUDIO_CACHE:
        return _AUDIO_CACHE[key]

    import edge_tts

    communicate = edge_tts.Communicate(cleaned, VOICE, rate=RATE, pitch=PITCH)
    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])

    if not chunks:
        raise RuntimeError("Không tạo được âm thanh.")

    audio = b"".join(chunks)
    _AUDIO_CACHE[key] = audio
    return audio
