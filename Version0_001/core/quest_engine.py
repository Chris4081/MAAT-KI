import json
import os
import datetime


class QuestEngine:

    def __init__(self, base_dir="data/quests"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        self.quest_file = os.path.join(self.base_dir, "quests.json")
        self._load()

    # --------------------------
    # INTERNAL LOAD/SAVE
    # --------------------------
    def _load(self):
        if not os.path.exists(self.quest_file):
            self.quests = []
            self._save()
        else:
            with open(self.quest_file, "r", encoding="utf-8") as f:
                self.quests = json.load(f)

    def _save(self):
        with open(self.quest_file, "w", encoding="utf-8") as f:
            json.dump(self.quests, f, indent=2, ensure_ascii=False)

    # --------------------------
    # PUBLIC API
    # --------------------------

    def add(self, quest_dict):
        """Manuell Quests hinzufügen – ID, text, xp, status=open"""
        self.quests.append(quest_dict)
        self._save()

    def list_open(self):
        return [q for q in self.quests if q.get("status") == "open"]

    def list_done(self):
        return [q for q in self.quests if q.get("status") == "done"]

    def list_all(self):
        return self.quests

    def complete(self, quest_id):
        for q in self.quests:
            if q.get("id") == quest_id:
                q["status"] = "done"
                q["completed_at"] = datetime.datetime.now().isoformat()
                self._save()
                return q
        return None

    # --------------------------
    # COMMAND HANDLER
    # --------------------------
    def handle(self, text):
        parts = text.split()

        # /quest → Übersicht
        if text.strip() == "/quest":
            return {
                "message": self._overview(),
                "reward_xp": None,
            }

        # /quest help
        if len(parts) >= 2 and parts[1] == "help":
            return {
                "message": self._help_text(),
                "reward_xp": None,
            }

        # /quest open
        if len(parts) >= 2 and parts[1] == "open":
            return {
                "message": self._list_open_text(),
                "reward_xp": None,
            }

        # /quest all
        if len(parts) >= 2 and parts[1] == "all":
            return {
                "message": self._list_all_text(),
                "reward_xp": None,
            }

        # /quest done
        if len(parts) >= 2 and parts[1] == "done":
            return {
                "message": self._list_done_text(),
                "reward_xp": None,
            }

        # /quest complete <id>
        if len(parts) >= 3 and parts[1] == "complete":
            qid = parts[2]
            q = self.complete(qid)
            if q:
                return {
                    "message": f"🎉 Quest abgeschlossen: {qid}",
                    "reward_xp": q.get("xp", 0),
                }
            else:
                return {
                    "message": f"❌ Keine Quest mit ID '{qid}' gefunden.",
                    "reward_xp": None,
                }

        # /quest <id> – Quest anzeigen
        if len(parts) == 2:
            qid = parts[1]
            q = next((x for x in self.quests if x.get("id") == qid), None)
            if not q:
                return {
                    "message": f"❌ Unbekannte Quest-ID '{qid}'.",
                    "reward_xp": None,
                }
            return {
                "message": self._show_quest(q),
                "reward_xp": None,
            }

        # Fallback
        return {
            "message": "❌ Unbekannter Quest-Befehl. Nutze /quest help.",
            "reward_xp": None,
        }

    # --------------------------
    # TEXT BUILDERS
    # --------------------------
    def _overview(self):
        lines = [
            "📜 MAAT-Quest-System\n",
            "Befehle:",
            "  /quest           – Übersicht",
            "  /quest help      – Hilfe",
            "  /quest open      – Liste offener Quests",
            "  /quest all       – Alle Quests",
            "  /quest done      – Abgeschlossene Quests",
            "  /quest complete <id> – Abschließen\n",
            "🔓 Offene Quests:"
        ]
        for q in self.list_open():
            lines.append(f"  - [{q['id']}] {q['text']}  (XP: {q.get('xp', 0)})")
        return "\n".join(lines)

    def _help_text(self):
        return self._overview()

    def _list_open_text(self):
        qs = self.list_open()
        if not qs:
            return "📭 Keine offenen Quests."
        lines = ["🔓 Offene Quests:"]
        for q in qs:
            lines.append(f"  - [{q['id']}] {q['text']} (XP: {q.get('xp',0)})")
        return "\n".join(lines)

    def _list_all_text(self):
        qs = self.list_all()
        if not qs:
            return "📭 Noch keine Quests."
        lines = ["📋 Alle Quests:"]
        for q in qs:
            lines.append(f"  - [{q['id']}] {q['text']} (Status: {q.get('status')})")
        return "\n".join(lines)

    def _list_done_text(self):
        qs = self.list_done()
        if not qs:
            return "✔️ Noch keine Quests abgeschlossen."
        lines = ["✔️ Erledigte Quests:"]
        for q in qs:
            lines.append(f"  - [{q['id']}] {q['text']} (XP: {q.get('xp',0)})")
        return "\n".join(lines)

    def _show_quest(self, q):
        return (
            f"🎯 Quest: {q['id']}\n"
            f"Beschreibung: {q['text']}\n"
            f"XP: {q.get('xp',0)}\n"
            f"Status: {q.get('status')}\n"
        )