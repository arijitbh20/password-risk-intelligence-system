import sqlite3

class Database:
    def __init__(self):

        self.conn = sqlite3.connect("../database/password.db", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

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

    def insert_log(self, risk, entropy, rules_score, breaches):

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
