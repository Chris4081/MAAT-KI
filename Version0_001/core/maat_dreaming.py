# core/maat_dreaming.py
# MAAT-KI – Nachtkonsolidierung („Maat-Dreaming“)

import sqlite3
import time
from datetime import datetime, timedelta
from collections import defaultdict

from core.semantic_memory import SemanticMemory

CATEGORY_KEYWORDS = {
    "beziehung": [
        "freund", "familie", "beziehung", "partner", "liebe",
        "hilfe", "du", "ich", "vertrauen", "nähe"
    ],
    "technik": [
        "ki", "ai", "modell", "programm", "algorithmus",
        "python", "llama", "gpu", "mac", "linux", "loader"
    ],
    "emotion": [
        "glücklich", "traurig", "angst", "wut",
        "freude", "hoffnung", "energie"
    ],
    "meta": [
        "bewusstsein", "philosophie", "maat", "harmonie",
        "balance", "kosmos", "universum"
    ],
    "projekt": [
        "maat-ki", "projekt", "github", "whitepaper", "buch",
        "mftoe", "string", "theorie"
    ],
}


def detect_category(text: str) -> str:
    text = (text or "").lower()
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for cat, words in CATEGORY_KEYWORDS.items():
        for w in words:
            if w in text:
                scores[cat] += 1

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "allgemein"


def compress_block(texts, max_len=300):
    """
    Ganz simple Verdichtung:
    - nimmt die wichtigsten Sätze/Wörter
    - beschneidet hart auf max_len Zeichen
    """
    joined = " ".join(t.strip() for t in texts if t and t.strip())
    if len(joined) <= max_len:
        return joined
    return joined[: max_len - 2] + " …"


class MaatDreaming:
    """
    Nachtkonsolidierung:
      - nimmt Episoden aus ltm
      - fasst pro Kategorie zusammen
      - schreibt Summaries in semantic_memory
      - lässt alte Erinnerungen langsam „ausblenden“
    """

    def __init__(self, db_path_ltm: str, db_path_semantic: str):
        self.db_path_ltm = db_path_ltm
        self.semantic = SemanticMemory(db_path_semantic)

    # --------------------------------------------------------
    # Hilfsfunktionen für DB
    # --------------------------------------------------------
    def _connect_ltm(self):
        return sqlite3.connect(self.db_path_ltm)

    # --------------------------------------------------------
    # Haupt-API
    # --------------------------------------------------------
    def run_night_cycle(
        self,
        hours_back: int = 24,
        max_episodes: int = 300,
        decay_factor: float = 0.997,
        delete_threshold: float = 0.02,
    ):
        """
        Führt einen „Traumzyklus“ durch:
          - Episoden der letzten X Stunden holen
          - nach Kategorie bündeln
          - Summaries in semantic_memory schreiben
          - priority in ltm leicht decayern
          - extrem schwache, alte Einträge optional löschen
        """
        now = time.time()
        min_ts = now - hours_back * 3600

        conn = self._connect_ltm()
        cur = conn.cursor()

        # 1. Relevante Episoden holen
        cur.execute(
            """
            SELECT id, ts, role, content, priority
            FROM ltm
            WHERE ts >= ?
            ORDER BY ts DESC
            LIMIT ?
            """,
            (min_ts, max_episodes),
        )
        rows = cur.fetchall()

        if not rows:
            conn.close()
            return "Keine Episoden für diesen Zeitraum gefunden."

        # 2. Nach Kategorie gruppieren
        by_cat = defaultdict(list)
        for _id, ts, role, content, prio in rows:
            cat = detect_category(content or "")
            by_cat[cat].append(
                {
                    "id": _id,
                    "ts": ts,
                    "role": role,
                    "content": content or "",
                    "priority": prio,
                }
            )

        # 3. Pro Kategorie eine Summary bauen & speichern
        dream_summaries = []
        for cat, items in by_cat.items():
            texts = [it["content"] for it in items]
            summary = compress_block(texts, max_len=400)
            if not summary:
                continue

            dream_text = f"[Maat-Dream:{cat}] {summary}"
            self.semantic.add(dream_text)  # geht in semantic_memory.db
            dream_summaries.append((cat, dream_text))

        # 4. Priority-Decay anwenden (alle Einträge leicht verblassen lassen)
        cur.execute("UPDATE ltm SET priority = priority * ?", (decay_factor,))

        # 5. Extrem schwache & alte Einträge löschen (Soft-Garbage-Collection)
        cutoff_ts = now - 7 * 24 * 3600  # älter als 7 Tage
        cur.execute(
            """
            DELETE FROM ltm
            WHERE ts < ? AND priority < ?
            """,
            (cutoff_ts, delete_threshold),
        )

        conn.commit()
        conn.close()

        # 6. Meta-„Traumlog“ in semantic_memory
        cats_str = ", ".join(cat for cat, _ in dream_summaries)
        meta_summary = (
            f"[Maat-Dream:meta] Nachtkonsolidierung abgeschlossen. "
            f"Kategorien in den letzten {hours_back}h: {cats_str or '—'}."
        )
        self.semantic.add(meta_summary)

        # Text für Terminal-Rückmeldung
        report_lines = ["🌙 Maat-Dreaming abgeschlossen:"]
        for cat, text in dream_summaries:
            report_lines.append(f"  • {cat}: {text[:80]}{'…' if len(text) > 80 else ''}")

        return "\n".join(report_lines)