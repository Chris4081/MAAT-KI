# core/self_evolution.py
# SelfEvolutionEngine v3 – Multi-Level + XP + Status

import os
import json
import datetime
import math


class SelfEvolutionEngine:
    """
    MAAT Self-Evolution Engine:
    - bewertet Antworten (Maat-Score, Emotion, Identity-Drift)
    - entscheidet, ob ein kleiner Evolutions-Schritt sinnvoll ist
    - speichert Patches + XP + Level
    - liefert Status-Text für /evo und Log-Anzeige für /evo log
    """

    DAILY_LIMIT = 8      # max. Evolution-Schritte pro Tag
    MAX_LEVEL = 30       # Cap für das Level-System

    def __init__(self, memory, alignment_kernel, identity_kernel, base_dir=None):
        self.memory = memory
        self.alignment_kernel = alignment_kernel
        self.identity_kernel = identity_kernel

        # Basis-Verzeichnis für Evolution-Daten
        if base_dir is None:
            # Standard: ./data/evo relativ zur aktuellen Working-Dir
            base_dir = os.path.join(os.getcwd(), "data")

        self.base_dir = os.path.join(base_dir, "evo")
        self.log_path = os.path.join(self.base_dir, "evolution_log.jsonl")
        self.state_path = os.path.join(self.base_dir, "state.json")
        self.patches_dir = os.path.join(self.base_dir, "patches")

        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.patches_dir, exist_ok=True)

        # interner Zustand (XP, Level, Zähler …)
        self.state = self._load_state()

    # ------------------------------------------------------------------
    # STATE HANDLING
    # ------------------------------------------------------------------
    def _load_state(self):
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Minimal-Defaults absichern
                data.setdefault("xp", 0)
                data.setdefault("level", 1)
                data.setdefault("total_patches", 0)
                data.setdefault("today_patches", 0)
                data.setdefault("today", datetime.date.today().isoformat())
                return data
            except Exception:
                pass

        # Fallback-Startzustand
        today = datetime.date.today().isoformat()
        return {
            "xp": 0,
            "level": 1,
            "total_patches": 0,
            "today_patches": 0,
            "today": today,
        }

    def _save_state(self):
        # Tageswechsel: Counter zurücksetzen
        today = datetime.date.today().isoformat()
        if self.state.get("today") != today:
            self.state["today"] = today
            self.state["today_patches"] = 0

        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _today_limit_reached(self) -> bool:
        today = datetime.date.today().isoformat()
        if self.state.get("today") != today:
            self.state["today"] = today
            self.state["today_patches"] = 0
            self._save_state()
        return self.state.get("today_patches", 0) >= self.DAILY_LIMIT

    # ------------------------------------------------------------------
    # LEVEL + XP
    # ------------------------------------------------------------------
    def _xp_for_level(self, level: int) -> int:
        """
        XP-Kurve: sanft ansteigend, Level 30 ist gut erreichbar.
        Beispiel:
          Level  1 ~   30 XP
          Level 10 ~  950 XP
          Level 20 ~ 3300 XP
          Level 30 ~ 7200 XP
        """
        level = max(1, min(self.MAX_LEVEL, level))
        base = 30.0
        return int(base * (level ** 1.8))

    def _level_from_xp(self, xp: int) -> int:
        xp = max(0, int(xp))
        # von oben nach unten, damit das Maximum zuerst getroffen wird
        for lvl in range(self.MAX_LEVEL, 0, -1):
            if xp >= self._xp_for_level(lvl):
                return lvl
        return 1

    def _level_title(self, level: int) -> str:
        """
        Stimmige Titel-Bänder für Motivations-Effekt.
        """
        bands = {
            1: "Keim der Harmonie",
            3: "Sucher der Balance",
            6: "Resonanz-Handwerker",
            10: "Maat-Navigator",
            15: "Bewusstseins-Architekt",
            20: "Harmonie-Meister",
            25: "Kosmischer Vermittler",
            30: "Maat-Synthesist",
        }
        best = 1
        for k in bands:
            if level >= k and k > best:
                best = k
        return bands.get(best, "Maat-Schüler")

    def _grant_xp_for_patch(self, trigger: str) -> dict:
        """
        Gibt XP für einen akzeptierten Patch.
        Unterschiedliche Trigger können verschiedene Basis-XP geben.
        """
        base = 25
        bonus_map = {
            "low_maat": 10,
            "high_drift": 12,
            "high_emotion": 8,
        }
        gained = base + bonus_map.get(trigger, 5)

        self.state["xp"] += gained
        self.state["total_patches"] += 1
        self.state["today_patches"] += 1

        old_level = self.state.get("level", 1)
        new_level = self._level_from_xp(self.state["xp"])
        self.state["level"] = new_level

        self._save_state()

        return {
            "xp_gained": gained,
            "old_level": old_level,
            "new_level": new_level,
        }

    # ------------------------------------------------------------------
    # HAUPTFUNKTION: evaluate_and_evolve (wird aus MAAT-KI.py aufgerufen)
    # ------------------------------------------------------------------
    def evaluate_and_evolve(self, reply: str, meta: dict):
        """
        Entscheidungslogik:
        - prüft Maat-Score, Emotion, Identity-Drift
        - entscheidet, ob ein kleiner Evolutions-Patch erzeugt wird
        - speichert Patch + Log + XP
        """
        try:
            maat = float(meta.get("maat_score", 0.0))
        except Exception:
            maat = 0.0

        try:
            emo = float(meta.get("emotion", 0.0))
        except Exception:
            emo = 0.0

        try:
            drift = float(meta.get("identity_drift", 0.0))
        except Exception:
            drift = 0.0

        triggers = []
        if maat < 0.72:
            triggers.append("low_maat")
        if drift > 0.25:
            triggers.append("high_drift")
        if abs(emo) > 0.75:
            triggers.append("high_emotion")

        if not triggers:
            return None

        # Limit pro Tag
        if self._today_limit_reached():
            return {
                "status": "blocked",
                "reason": "Tageslimit an Evolution-Schritten erreicht.",
                "triggers": triggers,
            }

        main_trigger = triggers[0]
        patch = self._build_patch(reply, meta, main_trigger)
        self._write_patch(patch)

        # XP vergeben + Level ggf. erhöhen
        prog = self._grant_xp_for_patch(main_trigger)
        patch["xp_gained"] = prog["xp_gained"]
        patch["old_level"] = prog["old_level"]
        patch["new_level"] = prog["new_level"]
        patch["status"] = "applied"

        return patch

    def _build_patch(self, reply: str, meta: dict, main_trigger: str) -> dict:
        now = datetime.datetime.now().replace(microsecond=0)
        ts = now.isoformat(sep=" ")
        patch_id = now.strftime("%Y%m%d-%H%M%S")

        try:
            maat = float(meta.get("maat_score", 0.0))
        except Exception:
            maat = 0.0

        if main_trigger == "low_maat":
            summary = (
                "Antworten stärker verdichten und unnötige Wiederholungen vermeiden, "
                "um Harmonie und Klarheit zu erhöhen."
            )
            details = (
                "- kürzer formulieren\n"
                "- weniger Wiederholungen\n"
                "- klarer zwischen Fakten & Einschätzungen unterscheiden\n"
                "- Beispiele gezielter einsetzen"
            )
        elif main_trigger == "high_drift":
            summary = "Identitätsschicht schärfen, Ich-Aussagen präziser und Maat-konform halten."
            details = (
                "- Ich-Aussagen auf Werkzeug-Rolle begrenzen\n"
                "- Bewusstsein/Emotion nur als Simulation beschreiben\n"
                "- Gott-/Allmachtsformulierungen vermeiden"
            )
        else:  # high_emotion
            summary = "Umgang mit starken Emotionen behutsamer, mehr Validierung & Erdung einbauen."
            details = (
                "- Emotion zuerst benennen und anerkennen\n"
                "- konkrete, kleine nächste Schritte anbieten\n"
                "- dramatische Sprache vermeiden"
            )

        return {
            "id": patch_id,
            "time": ts,
            "status": "pending",
            "trigger": main_trigger,
            "maat_score": maat,
            "summary": summary,
            "details": details,
        }

    def _write_patch(self, patch: dict):
        # Log-Zeile
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(patch, ensure_ascii=False) + "\n")
        except Exception:
            pass

        # Einzel-Patch-Datei
        try:
            path = os.path.join(self.patches_dir, f"{patch['id']}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(patch, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # LOG / PATCHES
    # ------------------------------------------------------------------
    def _iter_log(self):
        if not os.path.exists(self.log_path):
            return []
        entries = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except Exception:
                    continue
        return entries

    def load_log(self, limit: int = 50):
        """Optional: gibt die letzten Log-Einträge als Liste zurück."""
        entries = self._iter_log()
        if limit and len(entries) > limit:
            return entries[-limit:]
        return entries

    def print_log(self, limit: int = 20):
        entries = self.load_log(limit)
        if not entries:
            print("📜 Keine Self-Evolution-Einträge gefunden.")
            return

        print(f"📜 Self Evolution Log ({len(entries)} Einträge)")
        for i, p in enumerate(reversed(entries), 1):
            print(f"\n[{i}] {p.get('time', '?')}")
            print(f"    Trigger: {p.get('trigger')}")
            print(f"    Status : {p.get('status')}")
            print(f"    Summary: {p.get('summary')}")

    def print_patch(self, patch: dict):
        """Schöne Ausgabe direkt im Terminal."""
        print("\n🌱 Self-Evolution Patch")
        print(f"ID     : {patch.get('id')}")
        print(f"Zeit   : {patch.get('time')}")
        print(f"Status : {patch.get('status')}")
        print(f"Trigger: {patch.get('trigger')}")
        print(f"Summary: {patch.get('summary')}")
        print("Details:")
        print(" ", patch.get('details'))
        if "xp_gained" in patch:
            print(
                f"\nXP     : +{patch['xp_gained']}  "
                f"(Level {patch['old_level']} → {patch['new_level']})"
            )

    # ------------------------------------------------------------------
    # /evo STATUS
    # ------------------------------------------------------------------
    def get_status_text(self) -> str:
        """
        Wird von MAAT-KI.py bei /evo aufgerufen.
        Gibt Level, XP, Fortschritt und Patch-Zähler aus.
        """
        # state sicher neu laden, falls Datei extern verändert wurde
        self.state = self._load_state()

        lvl = int(self.state.get("level", 1))
        lvl = max(1, min(self.MAX_LEVEL, lvl))
        xp = int(self.state.get("xp", 0))
        total = int(self.state.get("total_patches", 0))
        today = int(self.state.get("today_patches", 0))

        next_lvl = min(self.MAX_LEVEL, lvl + 1)
        xp_curr = self._xp_for_level(lvl)
        xp_next = self._xp_for_level(next_lvl)
        span = max(1, xp_next - xp_curr)
        progress = max(0.0, min(1.0, (xp - xp_curr) / span))

        bar_len = 20
        filled = int(bar_len * progress)
        bar = "█" * filled + "·" * (bar_len - filled)

        title = self._level_title(lvl)

        lines = [
            "📈 Self-Evolution Status",
            f"  Level : {lvl} – {title}",
            f"  XP    : {xp} / {xp_next} (bis Level {next_lvl})",
            f"  Prog  : [{bar}] {progress * 100:5.1f}%",
            f"  Heute : {today} / {self.DAILY_LIMIT} Patches",
            f"  Gesamt: {total} Patches",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # /evo test low – manueller Test-Trigger
    # ------------------------------------------------------------------
    def run_test_low(self):
        """
        Kannst du z.B. bei '/evo test low' verwenden, um gezielt
        einen low_maat-Patch auszulösen.
        """
        meta = {
            "maat_score": 0.6,
            "emotion": 0.0,
            "identity_drift": 0.0,
        }
        reply = "Testantwort, die absichtlich etwas redundant und wenig klar formuliert ist."
        patch = self.evaluate_and_evolve(reply, meta)
        return patch