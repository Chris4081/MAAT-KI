# memory_narrative.py
# MAAT-KI - Memory Narrative Mode v1.0

import sqlite3
import time
from datetime import datetime

class MemoryNarrative:

    def __init__(self, db_path):
        self.db_path = db_path

    def fetch_recent(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT ts, role, compressed
            FROM ltm
            ORDER BY ts DESC
            LIMIT ?
        """, (limit,))

        rows = cur.fetchall()
        conn.close()
        return rows

    def build_narrative(self, limit=20):
        rows = self.fetch_recent(limit)

        if not rows:
            return "No memories found."

        blocks = []
        for ts, role, comp in rows:
            dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
            blocks.append(f"[{dt}] {role}: {comp}")

        # Finale Story
        story = "\n".join(blocks)

        return "📘 **Memory Narrative**\n\n" + story