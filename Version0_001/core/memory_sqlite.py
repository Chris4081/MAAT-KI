import sqlite3
import threading
import time


class SQLiteMemory:
    """
    Sehr einfache Memorieschicht, kompatibel mit MAAT-KI.
    Speichert Chat-Historie in einer SQLite Datenbank.
    """

    def __init__(self, db_path):
        self.db_path = db_path

        # VERBESSERUNG: connection + cursor persistent anlegen
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cur = self.conn.cursor()

        # Lock für Multi-Threading
        self.lock = threading.Lock()

        self._create_tables()
        self._run_migrations() 
    # --------------------------------------------------------------
    # DB SETUP
    # --------------------------------------------------------------
    def _create_tables(self):
        with self.lock:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()

    # Update DB

    def _run_migrations(self):
        """
        Upgrade bestehende memory.db automatisch,
        ohne Datenverlust.
        """
        try:
            # Prüfe, ob Spalte ts existiert
            self.cur.execute("PRAGMA table_info(memory);")
            cols = [row[1] for row in self.cur.fetchall()]

            # Falls keine ts-Spalte → hinzufügen
            if "ts" not in cols:
                print("[LTM] ✨ Migrating: Adding 'ts' column to memory table...")
                self.cur.execute("ALTER TABLE memory ADD COLUMN ts TEXT;")
                self.conn.commit()

                # Nachträglich alle alten Einträge mit Zeitstempel versehen
                self.cur.execute("UPDATE memory SET ts = datetime('now') WHERE ts IS NULL;")
                self.conn.commit()

                print("[LTM] ✅ Migration abgeschlossen: 'ts' Spalte hinzugefügt.")

        except Exception as e:
            print(f"[LTM MIGRATION ERROR] {e}")
    # --------------------------------------------------------------
    # SPEICHERN
    # --------------------------------------------------------------
    def add(self, role, content):
        """Speichert eine Chat-Nachricht (User oder Assistant)."""
        with self.lock:
            self.cur.execute(
                "INSERT INTO memory (role, content) VALUES (?, ?)",
                (role, content)
            )
            self.conn.commit()

    # --------------------------------------------------------------
    # LETZTER KONTEXT (für MAAT-KI Start)
    # --------------------------------------------------------------
    def last_context(self, limit=20):
        """Gibt die letzten N Nachrichten zurück als Textblock."""
        with self.lock:
            self.cur.execute(
                "SELECT role, content FROM memory ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = self.cur.fetchall()

        if not rows:
            return ""

        rows = rows[::-1]  # Chronologische Sortierung

        formatted = []
        for role, content in rows:
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)

    # --------------------------------------------------------------
    # LONG TERM SUPPORT: Direktzugriff für LTM
    # --------------------------------------------------------------
    def get_last_n(self, n=50):
        with self.lock:
            self.cur.execute(
                "SELECT id, role, content, ts FROM memory ORDER BY id DESC LIMIT ?",
                (n,)
            )
            rows = self.cur.fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "ts": row[3]
            })

        return results

    # --------------------------------------------------------------
    # SUCHEN (optional)
    # --------------------------------------------------------------
    def search(self, keyword, limit=5):
        with self.lock:
            self.cur.execute(
                "SELECT role, content, ts FROM memory WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
                (f"%{keyword}%", limit)
            )
            rows = self.cur.fetchall()

        results = []
        for r in rows:
            results.append({
                "role": r[0],
                "content": r[1],
                "ts": r[2]
            })

        return results

    # --------------------------------------------------------------
    # RESET
    # --------------------------------------------------------------
    def clear(self):
        with self.lock:
            self.cur.execute("DELETE FROM memory")
            self.conn.commit()

    # --------------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------------
    def close(self):
        try:
            self.conn.close()
        except:
            pass

    # --------------------------------------------------------------
    # ALLE EINTRÄGE LADEN  (/memory show)
    # --------------------------------------------------------------
    def get_all(self):
        with self.lock:
            self.cur.execute("SELECT id, role, content, ts FROM memory ORDER BY id ASC")
            rows = self.cur.fetchall()

        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "role": r[1],
                "content": r[2],
                "ts": r[3],
            })
        return results

    # --------------------------------------------------------------
    # EINEN EINTRAG LÖSCHEN  (/memory delete <id>)
    # --------------------------------------------------------------
    def delete(self, entry_id):
        with self.lock:
            self.cur.execute("DELETE FROM memory WHERE id = ?", (entry_id,))
            self.conn.commit()

    # --------------------------------------------------------------
    # MEMORY ALS LISTE FÜR DEBUG AUSGEBEN
    # --------------------------------------------------------------
    def count(self):
        with self.lock:
            self.cur.execute("SELECT COUNT(*) FROM memory")
            return self.cur.fetchone()[0]

    # ------------------------------------------------------------
    # 🔍 Suche nach Stichworten in den letzten X Einträgen
    #   (Kompatibel zu LongTermMemory.search_keyword)
    # ------------------------------------------------------------
    def search_recent_by_keywords(self, keyword, limit=3):
        """
        Sucht in den letzten gespeicherten Nachrichten nach einem Stichwort.
        Funktion dient als Fallback für ältere MAAT-KI Versionen, die diese Methode erwarten.
        """

        try:
            kw = f"%{keyword.lower()}%"
            self.cur.execute("""
                SELECT ts, role, content
                FROM memory
                WHERE LOWER(content) LIKE ?
                ORDER BY id DESC
                LIMIT ?
            """, (kw, limit))

            rows = self.cur.fetchall()

            return [
                {
                    "ts": r[0],
                    "role": r[1],
                    "content": r[2]
                }
                for r in rows
            ]
        except Exception as e:
            print(f"[SQLiteMemory SEARCH ERROR] {e}")
            return []