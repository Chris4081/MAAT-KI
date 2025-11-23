import sqlite3
import time

class EpisodicMemory:

    def __init__(self, db_path="episodic_memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        self._create_table()

    # -------------------------------------------------------------
    def _create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS episodic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL,
                role TEXT,
                text TEXT,
                priority REAL DEFAULT 1.0
            )
        """)
        self.conn.commit()

    # -------------------------------------------------------------
    def add(self, role, text, priority=1.0):
        ts = time.time()
        self.cur.execute(
            "INSERT INTO episodic (ts, role, text, priority) VALUES (?, ?, ?, ?)",
            (ts, role, text, priority)
        )
        self.conn.commit()

    # -------------------------------------------------------------
    def recall(self, query, limit=5):
        query = f"%{query.lower()}%"
        self.cur.execute("""
            SELECT ts, role, text, priority
            FROM episodic
            WHERE lower(text) LIKE ?
            ORDER BY priority DESC, ts DESC
            LIMIT ?
        """, (query, limit))
        rows = self.cur.fetchall()

        return [
            {
                "ts": ts,
                "role": role,
                "text": text,
                "priority": prio
            } for ts, role, text, prio in rows
        ]

    # -------------------------------------------------------------
    def decay(self, factor=0.995):
        """Menschliches Vergessen"""
        self.cur.execute("UPDATE episodic SET priority = priority * ?", (factor,))
        self.conn.commit()

    # -------------------------------------------------------------
    def clear(self):
        self.cur.execute("DELETE FROM episodic")
        self.conn.commit()