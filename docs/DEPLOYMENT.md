# Hướng dẫn chạy và deploy online

App này là FastAPI + HTML/CSS/JavaScript thuần. Khi deploy online, server Python sẽ phục vụ cả API và giao diện web.

## Chạy local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Mở trình duyệt:

```text
http://127.0.0.1:8000
```

## Kiểm tra trước khi deploy

```powershell
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

Nếu trả `"status": "ok"` và có số lượng `words`, `sentences`, `grammar_points`, `radicals`, nghĩa là app đã nạp dữ liệu.

## Deploy bằng Docker

Build image:

```powershell
docker build -t chinese-learning-app .
```

Chạy container:

```powershell
docker run --env-file .env -p 8000:8000 chinese-learning-app
```

Mở:

```text
http://127.0.0.1:8000
```

## Deploy lên Render

Repo đã có sẵn:

- `Dockerfile`
- `render.yaml`
- health check: `/api/health`

Các bước:

1. Đẩy project lên GitHub.
2. Vào Render, chọn New Blueprint hoặc New Web Service.
3. Chọn repo chứa project.
4. Render sẽ đọc `render.yaml` hoặc Dockerfile.
5. Sau khi deploy xong, mở URL Render cấp.

## Ghi chú về Google Sheet

Hiện app ưu tiên đọc Google Sheet online. Nếu Sheet chưa đọc được từ backend, app sẽ fallback về snapshot trong:

```text
data/local/*.tsv
```

Điều này giúp app vẫn chạy ổn trên online ngay cả khi Google Sheet chưa cấu hình OAuth hoặc chưa public đúng cách.

## Bước nâng cấp sau

- Thêm OAuth Google Sheet để đọc sheet private trực tiếp.
- Thêm database online để lưu tiến độ nhiều thiết bị.
- Thêm tài khoản người dùng nếu cần nhiều học viên.
