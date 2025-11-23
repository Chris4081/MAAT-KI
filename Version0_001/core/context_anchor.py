# context_anchor.py
# MAAT-KI — Context Anchor Engine v1.0

import sqlite3

class ContextAnchor:

    def __init__(self, db_path):
        self.db_path = db_path

    def reinforce(self, keyword, amount=1.1):
        """
        Verstärkt Erinnerungen, die zum Keyword passen.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            UPDATE ltm
            SET priority = priority * ?
            WHERE keywords LIKE ?
        """, (amount, f"%{keyword.lower()}%"))

        conn.commit()
        conn.close()

    def weaken_all(self, factor=0.999):
        """
        Globale Priorität senken – vergisst alte Erinnerungen langsam.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            UPDATE ltm SET priority = priority * ?
        """, (factor,))

        conn.commit()
        conn.close()