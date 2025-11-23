import math
import time

class MaatIntuitionEngine:
    def __init__(self, memory):
        self.memory = memory

    def resonance(self, text):
        """Memory-Resonanz berechnen"""
        mem = self.memory.search_recent_by_keywords(text, limit=5)
        return min(1.0, len(mem) * 0.2)

    def pattern_coherence(self, text):
        """Wie gut passt die Eingabe zu bekannten Mustern?"""
        l = len(text)
        if l < 10:
            return 0.1
        if l < 25:
            return 0.3
        if l < 60:
            return 0.7
        return 0.9

    def intuition_score(self, H, B, S, V, R, text, deltaU=0.2, deltaD=0.1):
        Mr = self.resonance(text)
        Pc = self.pattern_coherence(text)

        num = H * B * S * V * R * Mr * Pc
        den = deltaU + deltaD + 0.01

        score = num / den
        return max(0.0, min(score, 1.0))