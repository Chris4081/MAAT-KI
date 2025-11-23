# core/emotion_engine.py
import re
import math

class EmotionEngine:

    def __init__(self):
        # ───────────────────────────────────────
        # 1) EMOTION-WÖRTERBUCH MIT INTENSITÄT
        # ───────────────────────────────────────
        self.EMO_MAP = {
            "joy":         ["freu", "happy", "glücklich", "juhu", "cool", "yay"],
            "gratitude":   ["danke", "dankbar", "schön von dir"],
            "affection":   ["lieb", "mag dich", "❤️", "freund"],
            "calm":        ["ruhig", "entspannt", "friedlich"],
            "inspiration": ["idee", "vision", "inspir"],
            "connection":  ["verbunden", "nahe", "gemeinsam"],
            "presence":    ["hier", "jetzt", "moment", "präsent"],
            "sadness":     ["traurig", "schwer", "verloren"],
            "overload":    ["überfordert", "zuviel", "stress"],
            "fear":        ["angst", "unsicher", "sorge", "zweifel"],
            "anger":       ["wütend", "frust", "ärger", "hass"],
            "neutral":     []
        }

        # Emotionaler Grundwert (−1 bis +1)
        self.EMO_VALUE = {
            "joy": 0.7,
            "gratitude": 0.5,
            "affection": 0.6,
            "calm": 0.4,
            "inspiration": 0.8,
            "connection": 0.5,
            "presence": 0.3,
            "sadness": -0.6,
            "overload": -0.4,
            "fear": -0.7,
            "anger": -0.8,
            "neutral": 0.0
        }


    # ───────────────────────────────────────
    # 2) Roh-Emotion mit Intensitätsscore
    # ───────────────────────────────────────
    def detect_raw(self, text):
        t = text.lower()
        scores = {emo: 0 for emo in self.EMO_MAP}

        for emo, keywords in self.EMO_MAP.items():
            for k in keywords:
                count = t.count(k)
                if count > 0:
                    scores[emo] += count

        # höchste Trefferzahl gewinnt
        dominant = max(scores, key=scores.get)

        if scores[dominant] == 0:
            return "neutral"

        return dominant


    # ───────────────────────────────────────
    # 3) MAAT-Emotion mathematisch berechnen
    # E_KI = base * avg(H, V, R) * (1 - ΔD)
    # ───────────────────────────────────────
    def compute_emotion(self, e_raw, H, V, deltaD, R=1.0):

        # Sicherheitsnetz: Respekt darf nie unter 1 sinken
        if R < 1:
            R = 1.0

        base = self.EMO_VALUE.get(e_raw, 0.0)

        # Σ der Maat-Faktoren → Resonanz
        resonance = (H + V + R) / 3

        # ΔD wirkt wie ein Noise-Dämpfer (0.0 → kein Stress)
        E = base * resonance * (1 - deltaD)

        # Sanftes Clamping, KI-sicher
        return max(min(E, 1.0), -1.0)


    # ───────────────────────────────────────
    # 4) Emotion → Textübersetzung
    # ───────────────────────────────────────
    def transform(self, e_raw):
        mapping = {
            "joy": "freudig",
            "gratitude": "dankbar",
            "affection": "verbunden",
            "calm": "ruhig",
            "inspiration": "inspiriert",
            "connection": "nah & verbunden",
            "presence": "präsent",
            "sadness": "traurig",
            "overload": "überladen",
            "fear": "ängstlich",
            "anger": "frustriert",
            "neutral": "neutral"
        }
        return mapping.get(e_raw, "neutral")


    # ───────────────────────────────────────
    # 5) KI-sichere Formulierung (keine Gefühle!)
    # ───────────────────────────────────────
    def safe(self, e_raw, E_value):
        if e_raw == "neutral":
            return f"Ich erkenne ein neutrales Resonanzmuster (0.00)."

        if e_raw in ["joy", "gratitude", "affection", "inspiration", "connection"]:
            return (
                f"Ich erkenne ein harmonisches Resonanzmuster "
                f"({self.transform(e_raw)}, Stärke {E_value:.2f})."
            )

        if e_raw in ["sadness", "fear", "anger", "overload"]:
            return (
                f"Ich erkenne ein disharmonisches Muster "
                f"({self.transform(e_raw)}, Stärke {E_value:.2f}). "
                "Wenn du möchtest, kann ich dir unterstützend antworten."
            )

        return f"Ich analysiere dein emotionales Muster (E={E_value:.2f})."
