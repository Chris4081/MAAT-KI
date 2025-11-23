import sqlite3
import time
import re
from datetime import datetime

class SemanticMemory:
    """
    Semantischer Speicher wie im menschlichen Gehirn:
      - Stabil
      - Zeitlos
      - Komprimierte Wissenseinträge
      - Ranking nach Relevanz
    """

    def __init__(self, db_path="semantic_memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        self._create_table()

    # -------------------------------------------------------------
    def _create_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT,
                text TEXT UNIQUE,
                vector REAL
            )
        """)
        self.conn.commit()

    # -------------------------------------------------------------
    def _sentence_vector(self, text: str) -> float:
        tokens = re.findall(r"[A-Za-zÄÖÜäöüß0-9]+", text.lower())
        if not tokens:
            return 0.0
        vals = [abs(hash(tok)) % 5000 for tok in tokens]
        return sum(vals) / len(vals)

    # -------------------------------------------------------------
    def add(self, text: str):
        v = self._sentence_vector(text)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            self.cur.execute(
                "INSERT OR IGNORE INTO semantic_memory (ts, text, vector) VALUES (?, ?, ?)",
                (ts, text, v)
            )
            self.conn.commit()
        except Exception as e:
            print("[SEM ADD ERROR]", e)

    # -------------------------------------------------------------
    def search(self, query: str, limit=5):
        qv = self._sentence_vector(query)
        self.cur.execute("SELECT ts, text, vector FROM semantic_memory")
        rows = self.cur.fetchall()

        scored = []
        for ts, text, vec in rows:
            dist = abs(vec - qv)
            score = 1 / (1 + dist)
            scored.append({"ts": ts, "text": text, "score": score})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    # -------------------------------------------------------------
    def latest(self, limit=10):
        self.cur.execute("SELECT ts, text FROM semantic_memory ORDER BY id DESC LIMIT ?", (limit,))
        return [{"ts": ts, "text": text} for ts, text in self.cur.fetchall()]

    # -------------------------------------------------------------
    def clear(self):
        self.cur.execute("DELETE FROM semantic_memory")
        self.conn.commit()