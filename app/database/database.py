import sqlite3
from pathlib import Path
from app.core.config import DATABASE_PATH

if not DATABASE_PATH:
    raise ValueError(
        "DATABASE_PATH is not set. Add DATABASE_PATH=database/password.db to the .env file."
    )

path = Path(__file__).resolve().parents[2] / DATABASE_PATH

class Database:
    def __init__(self):

        try:
            self.conn = sqlite3.connect(path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise RuntimeError(f"Could not connect to database at {path}: {e}") from e

    def create_table(self):

        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                risk_status TEXT NOT NULL,
                breach_count INTEGER,          
                score INTEGER NOT NULL,
                entropy REAL NOT NULL
            )
        """)

    def insert_log(self, risk, breaches, rules_score, entropy):

        with self.conn:
            self.conn.execute("""
            INSERT INTO logs (risk_status, breach_count, score, entropy)
            VALUES (?, ?, ?, ?)
        """, (risk, breaches, rules_score, entropy))

    def fetch_data(self):

        rows = self.conn.execute("SELECT * FROM logs ORDER BY timestamp DESC").fetchall()
        return [dict(row) for row in rows]

    def close_connection(self):

        self.conn.close()