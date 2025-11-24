import math
import time

class MaatIntuitionEngine:
    """
    Maat Intuition Engine (MIE)
    ---------------------------
    Berechnet die intuitive Einschätzung einer Eingabe basierend auf:

    - H, B, S, V, R  (ethische Maat-Felder)
    - Memory-Resonanz
    - Muster-Kohärenz
    - Delta-Werte (Unsicherheit / Drift)

    Alle Scores werden automatisch zwischen 0 und 1 gehalten.
    """

    def __init__(self, memory):
        self.memory = memory

    # -----------------------------------------------------
    # Memory-Resonanz
    # -----------------------------------------------------
    def resonance(self, text):
        """
        Memory-Resonanz:
        Wie stark die Eingabe mit dem gespeicherten Wissen übereinstimmt.
        Wertebereich: 0.0 – 1.0
        """

        if not self.memory:
            return 0.2  # Baseline-Resonanz

        hits = self.memory.search_recent_by_keywords(text, limit=10)

        # qualitative Resonanz: häufigere Treffer → stärkere Resonanz
        raw = len(hits)

        # Sanfte Kurve statt Sprüngen
        resonance = 1 - math.exp(-raw / 3)

        return max(0.0, min(resonance, 1.0))

    # -----------------------------------------------------
    # Musterkohärenz (Pattern Coherence)
    # -----------------------------------------------------
    def pattern_coherence(self, text):
        """
        Wie gut passt die Eingabe zu bekannten sprachlichen Mustern?
        Nutzt eine logarithmische Kurve statt harter Grenzen.
        """

        length = len(text.strip())

        if length <= 0:
            return 0.1

        # logarithmisch: lange, kohärente Texte geben sanft höheren Score
        pc = min(1.0, math.log(length + 1, 60))

        # Untergrenze
        return max(0.1, pc)

    # -----------------------------------------------------
    # Intuition Score
    # -----------------------------------------------------
    def intuition_score(
        self,
        H,
        B,
        S,
        V,
        R,
        text,
        deltaU=0.2,
        deltaD=0.1,
    ):
        """
        Berechnet den finalen Intuitions-Score.
        """

        Mr = self.resonance(text)
        Pc = self.pattern_coherence(text)

        # Sicherheit: Werte normalisieren
        H = max(0, min(H, 1))
        B = max(0, min(B, 1))
        S = max(0, min(S, 1))
        V = max(0, min(V, 1))
        R = max(0, min(R, 1))

        num = H * B * S * V * R * Mr * Pc
        den = max(deltaU + deltaD + 0.01, 0.01)

        score = num / den

        # Endgültig clampen
        score = max(0.0, min(score, 1.0))

        return score