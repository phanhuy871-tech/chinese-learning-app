# Chinese Learning App

Khung ứng dụng học tiếng Trung bằng Python/FastAPI, dùng Google Sheet làm nguồn dữ liệu và chia riêng data, logic, game, giao diện.

## Chạy local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mở:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

## Test

```powershell
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Deploy online

Project có sẵn `Dockerfile`, `.dockerignore`, `render.yaml` và health check `/api/health`.

Xem hướng dẫn chi tiết tại:

```text
docs/DEPLOYMENT.md
```

## Google Sheet

App đọc sheet công khai qua CSV export:

```text
https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}
```

Các cột nên có:

```text
id, hanzi, pinyin, pinyin_no_tone, meaning_vi, meaning_en,
word_type, level, lesson, topic, audio_url, image_url,
example_sentence_hanzi, example_sentence_pinyin, example_sentence_vi,
difficulty, tags, is_active
```

Cho dữ liệu câu:

```text
sentence_hanzi, sentence_pinyin, sentence_vi, words,
blank_sentence, blank_answer_hanzi, grammar_point
```

`words` có thể nhập dạng:

```text
我|喜欢|学习|中文
```

## Module chính

```text
app/data_sources/google_sheets  # lấy và chuẩn hóa dữ liệu sheet
app/vocabulary                  # từ vựng
app/sentences                   # câu
app/games                       # logic game
app/learning                    # điểm, tiến độ học
app/web                         # giao diện web
app/api                         # API JSON
```
