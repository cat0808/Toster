import sqlite3
from contextlib import closing

DB_PATH = "bot.db"

# Все .db файлы(базы данных) отсутствуют в репозитории для безопасности

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row  # строки как словари - row["username"]
    return conn

def init_db():
    with closing(get_connection()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,          -- Telegram user id
                username TEXT,
                first_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

def add_user(user_id, username, first_name):
    with closing(get_connection()) as conn:
        conn.execute(
            """
            INSERT INTO users (id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (user_id, username, first_name),
        )
        conn.commit()

def get_user(user_id):
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()