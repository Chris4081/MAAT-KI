# long_term_memory.py
# MAAT-KI — Long Term Memory v5.0 (clean, stable)

import sqlite3
import time
import re

# ------------------------------------------------
# Keyword Extraktion
# ------------------------------------------------
def extract_keywords(text):
    stop = {
        "ich","du","der","die","das","ein","eine","und","oder","aber","mit",
        "für","auf","in","am","von","zu","ist","war","sind","sein","habe",
        "hat","haben","dass","ohne"
    }
    text = text.lower()
    words = re.findall(r"[a-zA-Zäöüß]+", text)
    words = [w for w in words if w not in stop]
    words = sorted(words, key=lambda x: -len(x))
    return words[:3] if words else ["none"]

# ------------------------------------------------
# Auto-Kategorie
# ------------------------------------------------
CATEGORY_KEYWORDS = {
    "beziehung": ["freund","familie","partner","liebe","vertrauen","nähe"],
    "technik":   ["ki","ai","modell","python","gpu","mac","linux"],
    "emotion":   ["glücklich","traurig","angst","energie","freude"],
    "meta":      ["bewusstsein","philosophie","maat","harmonie","balance"],
    "projekt":   ["maat-ki","github","whitepaper","buch","theorie"]
}

def detect_category(text):
    text = text.lower()
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in text:
                scores[cat] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "allgemein"

# ------------------------------------------------
# Compression
# ------------------------------------------------
def compress_text(text):
    words = text.split()
    out = []
    seen = set()
    for w in words:
        lw = w.lower()
        if lw not in seen:
            out.append(w)
            seen.add(lw)
    compressed = " ".join(out)
    if len(compressed) > 300:
        compressed = compressed[:300] + " …"
    return compressed

# ------------------------------------------------
# LongTermMemory (SQLite)
# ------------------------------------------------
class LongTermMemory:

    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ltm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL,
            role TEXT,
            content TEXT,
            compressed TEXT,
            keywords TEXT,
            category TEXT
        )
        """)
        conn.commit()
        conn.close()

    # ------------------------------------------------
    # Add
    # ------------------------------------------------
    def add(self, role, content):
        ts = time.time()
        kws = ",".join(extract_keywords(content))
        category = detect_category(content)
        comp = compress_text(content)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ltm (ts, role, content, compressed, keywords, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ts, role, content, comp, kws, category))
        conn.commit()
        conn.close()

    # ------------------------------------------------
    # Keyword Suche
    # ------------------------------------------------
    def search_keyword(self, query, limit=5):
        pattern = f"%{query.lower()}%"
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT ts, role, content, compressed, category
            FROM ltm
            WHERE LOWER(content) LIKE ?
            ORDER BY ts DESC
            LIMIT ?
        """, (pattern, limit))
        rows = cur.fetchall()
        conn.close()

        return [
            {
                "ts": r[0],
                "role": r[1],
                "content": r[2],
                "compressed": r[3],
                "category": r[4],
            }
            for r in rows
        ]

    # ------------------------------------------------
    # Hybrid Recall (Keyword + Semantik)
    # ------------------------------------------------
    def recall(self, query, limit=10):
        try:
            k_hits = self.search_keyword(query, limit)
        except:
            k_hits = []

        results = []
        seen = set()
        for r in k_hits:
            key = r["compressed"]
            if key not in seen:
                results.append(r)
                seen.add(key)
        return results[:limit]