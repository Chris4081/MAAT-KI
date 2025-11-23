# core/emotion_maat_mapper.py
# Emotion-Maat-Mapper (EMM) – v1.0
# Wandelt erkannte Emotionen in Maat-Vektor-Weights um

import math
from typing import Dict

class EmotionMaatMapper:
    """
    Emotion → Maat-Vektor Transformation
    Nutzt die fünf Maat-Prinzipien:
    H, B, S, V, R

    Idee:
    Jede Emotion verändert den Fokus der KI.
    Beispiel:
        - Trauer → mehr Verbundenheit + Respekt
        - Freude → mehr Schöpfungskraft + Harmonie
        - Angst → mehr Balance + Respekt
        - Wut → mehr Balance + Harmonie (Stabilisierung)
    """

    def __init__(self):
        # Grundgewichtung (Neutral)
        self.default_weights = {
            "H": 1.0,
            "B": 1.0,
            "S": 1.0,
            "V": 1.0,
            "R": 1.0,
        }

    # -------------------------------------------------------------
    # Hauptfunktion: Emotion → Maat-Vektor
    # -------------------------------------------------------------
    def map(self, emotion: str, intensity: float = 0.0) -> Dict[str, float]:
        """
        emotion = erkannte Emotion (z.B. 'joy', 'sadness', 'fear')
        intensity = 0.0 – 1.0
        """

        e = emotion.lower().strip()
        w = self.default_weights.copy()

        # kleine Sicherheit
        intensity = max(0.0, min(1.0, intensity))

        # ---------------------------------------------------------
        # Emotion → Fokus
        # ---------------------------------------------------------
        if e in ["joy", "happy", "glad", "freude"]:
            w["H"] += 0.4 * intensity
            w["S"] += 0.5 * intensity
            w["V"] += 0.3 * intensity

        elif e in ["sadness", "sad", "trauer"]:
            w["V"] += 0.6 * intensity
            w["R"] += 0.5 * intensity
            w["H"] += 0.2 * intensity

        elif e in ["fear", "angst"]:
            w["B"] += 0.6 * intensity
            w["R"] += 0.4 * intensity

        elif e in ["anger", "wut"]:
            w["B"] += 0.7 * intensity
            w["H"] += 0.5 * intensity

        elif e in ["surprise", "überraschung"]:
            w["S"] += 0.6 * intensity
            w["H"] += 0.3 * intensity

        elif e in ["disgust", "ekel"]:
            w["R"] += 0.7 * intensity
            w["B"] += 0.4 * intensity

        else:
            # neutral → leicht ausgeglichen
            w["H"] += 0.1
            w["B"] += 0.1

        # Normalisierung (nicht zu stark verzerren)
        scale = sum(w.values())
        for k in w:
            w[k] = w[k] / scale

        return w