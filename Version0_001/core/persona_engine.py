import json
import os
import datetime
import math


class PersonaEngine:
    """
    MAAT-Persona Engine v1
    ----------------------
    Eine dynamische, lernfähige Persönlichkeit für Maatis.
    - besitzt Kernwerte (H,B,S,V,R)
    - besitzt Soft-Traits (Neugier, Ruhe, Tiefe, Humor)
    - reagiert auf Emotionen, Quests, XP & Nutzerverhalten
    - speichert Entwicklung persistiert in persona.json
    """

    def __init__(self, base_dir="data/persona"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        self.path = os.path.join(self.base_dir, "persona.json")
        self.state = self._load()

    # -------------------------------------------------
    # LOAD / SAVE
    # -------------------------------------------------
    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass

        # Erststart → Grundeinstellungen
        return {
            "created": datetime.datetime.now().isoformat(),
            "core": {
                "harmonie": 0.75,
                "balance": 0.75,
                "schoepfung": 0.80,
                "verbindung": 0.70,
                "respekt": 0.85
            },
            "traits": {
                "curiosity": 0.6,
                "calmness": 0.5,
                "humor": 0.3,
                "depth": 0.7
            },
            "style_bias": {
                "short": 0.5,
                "long": 0.5,
                "warm": 0.7,
                "analytical": 0.6
            },
            "history": []
        }

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    # -------------------------------------------------
    # UPDATE THROUGH INTERACTION
    # -------------------------------------------------
    def update_from_emotion(self, emotion, intensity):
        """
        Emotion beeinflusst Traits.
        """
        t = self.state["traits"]

        if emotion in ["joy", "gratitude", "affection", "connection"]:
            t["curiosity"] += 0.01 * intensity
            t["calmness"] += 0.005 * intensity
        elif emotion in ["sadness", "fear"]:
            t["depth"] += 0.01 * abs(intensity)
            t["calmness"] -= 0.005 * abs(intensity)

        # clamp
        for k in t:
            t[k] = max(0.0, min(1.0, t[k]))

        self._save()

    def update_from_quest(self, quest_id, xp):
        """
        Quests verändern Soft-Persönlichkeit.
        """
        t = self.state["traits"]
        c = self.state["core"]

        if quest_id.startswith("harmony"):
            c["harmonie"] += xp / 3000
            t["calmness"] += xp / 6000

        elif quest_id.startswith("creativity"):
            c["schoepfung"] += xp / 3000
            t["curiosity"] += xp / 5000

        elif quest_id.startswith("connection"):
            c["verbindung"] += xp / 3000
            t["depth"] += xp / 6000

        elif quest_id.startswith("respect"):
            c["respekt"] += xp / 3000
            t["calmness"] += xp / 6000

        # clamp
        for k in c:
            c[k] = max(0.01, min(1.5, c[k]))

        for k in t:
            t[k] = max(0.0, min(1.0, t[k]))

        # Verlauf sichern
        self.state["history"].append({
            "ts": datetime.datetime.now().isoformat(),
            "event": f"quest:{quest_id}",
            "xp": xp
        })

        self._save()

    # -------------------------------------------------
    # PERSONALITY MODIFIERS FOR WRITING STYLE
    # -------------------------------------------------
    def get_style_bias(self):
        return self.state["style_bias"]

    def get_trait_snapshot(self):
        return self.state["traits"]

    def get_personality_signature(self):
        c = self.state["core"]
        t = self.state["traits"]

        return {
            "temperament": {
                "calm": t["calmness"],
                "curious": t["curiosity"],
                "deep": t["depth"],
                "humorous": t["humor"]
            },
            "ethical": {
                "H": c["harmonie"],
                "B": c["balance"],
                "S": c["schoepfung"],
                "V": c["verbindung"],
                "R": c["respekt"]
            },
        }