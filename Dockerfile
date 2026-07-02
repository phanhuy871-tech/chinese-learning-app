# Image Python gọn để chạy FastAPI trên server online.
FROM python:3.12-slim

# Không tạo file .pyc và cho log in ra ngay, tiện debug khi deploy.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài dependency trước để Docker cache tốt hơn khi chỉ sửa code.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source app, snapshot data và tài liệu cần thiết.
COPY app ./app
COPY data ./data
COPY docs ./docs
COPY README.md .
COPY .env.example .

EXPOSE 8000

# Render/Railway/Fly thường truyền PORT qua biến môi trường.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
