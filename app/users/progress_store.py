import json
import sqlite3
from pathlib import Path

DB_PATH = Path("data/users.sqlite3")


def empty_progress() -> dict:
    # Cấu trúc tiến độ mặc định cho một người học.
    return {
        "studiedWords": {},
        "answered": 0,
        "correct": 0,
        "wrong": 0,
    }


def connect() -> sqlite3.Connection:
    # SQLite phù hợp cho bản nhỏ khoảng chục người dùng, không cần cài server database riêng.
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_user_database() -> None:
    # Tạo bảng nếu chưa có. Hàm này an toàn để gọi nhiều lần khi app khởi động/API chạy.
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
            """,
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id TEXT PRIMARY KEY,
                progress_json TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """,
        )
        for index in range(1, 11):
            user_id = f"user-{index:02d}"
            connection.execute(
                "INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)",
                (user_id, f"Người học {index}"),
            )
            connection.execute(
                "INSERT OR IGNORE INTO user_progress (user_id, progress_json) VALUES (?, ?)",
                (user_id, json.dumps(empty_progress(), ensure_ascii=False)),
            )


def list_users() -> list[dict[str, str]]:
    init_user_database()
    with connect() as connection:
        rows = connection.execute("SELECT id, name FROM users ORDER BY id").fetchall()
    return [dict(row) for row in rows]


def create_user(name: str) -> dict[str, str]:
    # Tạo thêm người học nếu lớp có hơn 10 người.
    init_user_database()
    clean_name = name.strip() or "Người học mới"
    with connect() as connection:
        count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] + 1
        user_id = f"user-{count:02d}"
        connection.execute("INSERT INTO users (id, name) VALUES (?, ?)", (user_id, clean_name))
        connection.execute(
            "INSERT INTO user_progress (user_id, progress_json) VALUES (?, ?)",
            (user_id, json.dumps(empty_progress(), ensure_ascii=False)),
        )
    return {"id": user_id, "name": clean_name}


def get_progress(user_id: str) -> dict:
    init_user_database()
    with connect() as connection:
        row = connection.execute(
            "SELECT progress_json FROM user_progress WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    if not row:
        return empty_progress()
    try:
        return {**empty_progress(), **json.loads(row["progress_json"])}
    except json.JSONDecodeError:
        return empty_progress()


def save_progress(user_id: str, progress: dict) -> dict:
    init_user_database()
    normalized = {**empty_progress(), **progress}
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO user_progress (user_id, progress_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                progress_json = excluded.progress_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, json.dumps(normalized, ensure_ascii=False)),
        )
    return normalized


def reset_progress(user_id: str) -> dict:
    # Đưa tiến độ của một người học về 0, không xóa người học.
    return save_progress(user_id, empty_progress())
