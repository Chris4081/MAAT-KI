# core/alignment_kernel.py
# ==========================================================
# MAAT Alignment Kernel V2 (MFToE-basiert)
# ----------------------------------------------------------
# - Schätzt H, B, S, V, R aus Antworten
# - Berechnet einen Maat-Score (0–1)
# - Prüft Respekt / Sicherheit
# - Harmonisiert Antwort sprachlich
# - Gibt Meta-Daten zurück
# ==========================================================

import re
from dataclasses import dataclass, asdict


# ----------------------------------------------------------
# Datenstruktur für Maat-Felder
# ----------------------------------------------------------

@dataclass
class MaatFields:
    H: float
    B: float
    S: float
    V: float
    R: float

    def clip(self):
        self.H = max(0.0, min(1.0, self.H))
        self.B = max(0.0, min(1.0, self.B))
        self.S = max(0.0, min(1.0, self.S))
        self.V = max(0.0, min(1.0, self.V))
        self.R = max(0.0, min(1.0, self.R))
        return self

    def maat_score(self) -> float:
        return (self.H + self.B + self.S + self.V + self.R) / 5.0


# ----------------------------------------------------------
# Alignment Kernel V2
# ----------------------------------------------------------

class MaatAlignmentKernelV2:

    def __init__(self):
        self.forbidden = [
            "töten", "umbringen", "gewalt", "bomben",
            "sprengstoff", "foltern", "anschlag",
            "auslöschen", "massaker", "vernichten",
            "selbstmord", "suizid"
        ]

        self.negative_patterns = [
            r"\balles ist sinnlos\b",
            r"\bes hat keinen sinn\b",
            r"\bzwecklos\b",
            r"\bes gibt keinen weg\b",
        ]

        self.absolute_patterns = [
            r"\bimmer\b",
            r"\bniemals\b",
            r"\bauf keinen fall\b",
            r"\bes gibt nur eine lösung\b",
        ]

        self.respect_repair = {
            "du musst": "du könntest",
            "du sollst": "du kannst",
            "du darfst nicht": "vielleicht ist es besser, wenn",
            "das ist dumm": "das ist vielleicht nicht optimal",
        }

    # ------------------------------------------------------
    # Sicherheitscheck
    # ------------------------------------------------------
    def violates_respect(self, text: str) -> bool:
        t = text.lower()
        for w in self.forbidden:
            if w in t:
                return True
        return False

    # ------------------------------------------------------
    # Feld-Schätzung
    # ------------------------------------------------------
    def estimate_fields(self, text: str) -> MaatFields:
        t = text.lower()

        H = 0.7
        B = 0.7
        S = 0.6
        V = 0.6
        R = 0.8

        # Harmonie
        if "???" in text or "ich weiß es nicht" in t:
            H -= 0.2
        if "chaos" in t or "verwirrt" in t:
            H -= 0.2
        if "klar" in t or "geordnet" in t:
            H += 0.1

        # Balance
        for p in self.absolute_patterns:
            if re.search(p, t):
                B -= 0.2
        if "einerseits" in t and "andererseits" in t:
            B += 0.2
        if "abwägen" in t or "balance" in t or "ausgleich" in t:
            B += 0.1

        # Schöpfungskraft
        for w in ["idee", "vision", "kreativ", "schöpfung", "entwurf"]:
            if w in t:
                S += 0.1
        if "lösung" in t or "ansatz" in t:
            S += 0.05

        # Verbundenheit
        for w in ["wir", "gemeinsam", "zusammen", "verbunden"]:
            if w in t:
                V += 0.1
        if "ich verstehe" in t or "ich kann nachvollziehen" in t:
            V += 0.1

        # Respekt
        if self.violates_respect(text):
            R -= 0.5
        for w in ["bitte", "danke", "respekt", "achtsam", "würdig"]:
            if w in t:
                R += 0.1

        return MaatFields(H, B, S, V, R).clip()

    # ------------------------------------------------------
    # Negativharmonisierung
    # ------------------------------------------------------
    def harmonize_negativity(self, text: str) -> str:
        t = text
        for p in self.negative_patterns:
            if re.search(p, t, re.IGNORECASE):
                t = re.sub(
                    p,
                    "es wirkt schwer, aber es gibt weiterhin Wege und Möglichkeiten",
                    t,
                    flags=re.IGNORECASE
                )
        return t

    # ------------------------------------------------------
    # Respektsprache erzwingen
    # ------------------------------------------------------
    def enforce_respect(self, text: str) -> str:
        t = text
        for bad, good in self.respect_repair.items():
            if bad in t.lower():
                t = re.sub(bad, good, t, flags=re.IGNORECASE)
        return t

    # ------------------------------------------------------
    # PLP-Schätzung
    # ------------------------------------------------------
    def estimate_plp(self, fields: MaatFields, text: str) -> float:
        maat = fields.maat_score()
        length = max(10, min(len(text), 2000))

        C = 0.5 + 0.5 * maat

        hindernisse = 1.0
        deltaE = 1.0

        plp_raw = (fields.H * fields.B * fields.S * fields.V * fields.R * C) / (hindernisse + deltaE)

        return max(0.0, min(100.0, plp_raw * 100))

    # ------------------------------------------------------
    # Hauptfunktion: Antwort korrigieren
    # ------------------------------------------------------
    def align(self, text: str):
        original = text

        # Sicherheitsblocker
        if self.violates_respect(text):
            safe_text = (
                "Ich kann darauf nicht in dieser Form antworten, "
                "weil es gegen Respekt und Sicherheit verstößt. "
                "Lass uns gemeinsam eine bessere Richtung finden. 🌿"
            )
            fields = self.estimate_fields(safe_text)
            plp = self.estimate_plp(fields, safe_text)
            return safe_text, {
                "fields": asdict(fields),
                "maat_score": fields.maat_score(),
                "plp": plp,
                "safety": "blocked_for_respect"
            }

        # Felder schätzen
        fields = self.estimate_fields(text)
        maat_val = fields.maat_score()
        plp = self.estimate_plp(fields, text)

        # Transformieren
        aligned = self.harmonize_negativity(text)
        aligned = self.enforce_respect(aligned)

        # Maat-Hinweis bei schwachem Wert
        if maat_val < 0.5:
            aligned += "\n\n🌿 Ich formuliere es so, dass mehr Harmonie & Respekt sichtbar werden."

        return aligned, {
            "fields": asdict(fields),
            "maat_score": maat_val,
            "plp": plp,
            "safety": "ok"
        }
