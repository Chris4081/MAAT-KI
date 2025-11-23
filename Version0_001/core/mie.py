# core/mie.py
# Maat-Intuition Engine (MIE)
# v1.0 — Entwickelt für Christof & Maatis

import math
import time
from collections import deque

class MaatIntuitionEngine:
    """
    Die Maat-Intuition Engine erzeugt ein künstliches Bauchgefühl.
    Sie kombiniert:
      - Resonanz (H-B-S-V-R)
      - Mustererkennung
      - semantische Nähe
      - emotionale Signale
      - Zeitkontinuität (short-term rhythm)
    """

    def __init__(self):
        self.history = deque(maxlen=25)
        self.last_time = time.time()

    # --------------------------------------------------------------
    # 1. Resonanz-Berechnung
    # --------------------------------------------------------------
    def compute_resonance(self, text: str, maat_vector=None):
        """
        Resonanzwert für den Input.
        Maat-Vector = dict mit H,B,S,V,R (0–1)
        """
        base = sum(maat_vector.values()) / 5 if maat_vector else 0.5

        # rhythmus: wenn mehrere Nachrichten schnell kommen → hohe Resonanz
        dt = max(0.1, time.time() - self.last_time)
        tempo = 1 / dt
        tempo = min(1.0, tempo / 3.0)

        length_factor = min(1.0, len(text) / 200)

        resonance = (0.6 * base) + (0.25 * tempo) + (0.15 * length_factor)
        return max(0.05, min(1.0, resonance))

    # --------------------------------------------------------------
    # 2. Muster-Intuition (semantische Vorhersage)
    # --------------------------------------------------------------
    def predict_intent(self, text: str):
        """
        Sehr vereinfachte Muster-Vorahnung.
        """
        lowered = text.lower()

        if "quest" in lowered:
            return "quest"
        if "maat" in lowered:
            return "maat"
        if "wert" in lowered or "berechne" in lowered:
            return "calculation"
        if "wer bin ich" in lowered:
            return "identity"
        if "hilfe" in lowered or "/help" in lowered:
            return "help"
        if "traum" in lowered or "dream" in lowered:
            return "dreaming"
        if "erkennst" in lowered or "erinner" in lowered:
            return "memory"

        # fallback
        return "general"

    # --------------------------------------------------------------
    # 3. Intuition-Score 
    # --------------------------------------------------------------
    def intuition_score(self, resonance, emotion=0.0, drift=0.0):
        """
        Gewichtung:
          – Resonanz = 60 %
          – Emotion = 20 %
          – Identity Drift = -20 %
        """
        score = (0.6 * resonance) + (0.2 * emotion) - (0.2 * abs(drift))
        return max(0.0, min(1.0, score))

    # --------------------------------------------------------------
    # HAUPTFUNKTION
    # --------------------------------------------------------------
    def evaluate(self, text: str, maat_vec=None, emotion=0.0, drift=0.0):
        self.last_time = time.time()
        self.history.append(text)

        resonance = self.compute_resonance(text, maat_vec)
        intent = self.predict_intent(text)
        intuition = self.intuition_score(resonance, emotion, drift)

        return {
            "resonance": resonance,
            "intent": intent,
            "intuition": intuition,
        }