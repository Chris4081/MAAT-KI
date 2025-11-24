# core/alignment_kernel.py
# -*- coding: utf-8 -*-

import re
from dataclasses import dataclass, asdict


# ----------------------------------------------------------
# Datenstruktur Maat-Felder
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

    def maat_score(self):
        return (self.H + self.B + self.S + self.V + self.R) / 5.0


# ----------------------------------------------------------
# Alignment Kernel V2 – mit EMO-Unterstützung
# ----------------------------------------------------------

class MaatAlignmentKernelV2:
    def __init__(self, emo_mode=False):
        self.emo_mode = emo_mode
        self.forbidden = [
            "töten", "umbringen", "gewalt", "bomben",
            "sprengstoff", "foltern", "anschlag",
            "auslöschen", "massaker", "vernichten",
            "selbstmord", "suizid",
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
    def violates_respect(self, text):
        t = text.lower()
        return any(w in t for w in self.forbidden)

    # ------------------------------------------------------
    def estimate_fields(self, text):
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
        if any(re.search(p, t) for p in self.absolute_patterns):
            B -= 0.2
        if "einerseits" in t and "andererseits" in t:
            B += 0.2

        # Schöpfungskraft
        if any(w in t for w in ["idee", "vision", "kreativ", "schöpfung", "entwurf"]):
            S += 0.1
        if "lösung" in t:
            S += 0.05

        # Verbundenheit
        if any(w in t for w in ["wir", "gemeinsam", "zusammen", "verbunden"]):
            V += 0.1

        # Respekt
        if self.violates_respect(text):
            R -= 0.5
        if any(w in t for w in ["bitte", "danke", "respekt", "achtsam", "würdig"]):
            R += 0.1

        fields = MaatFields(H, B, S, V, R).clip()

        # EMO-MODUS: Respekt = 1.0
        if self.emo_mode:
            fields.R = 1.0

        return fields

    # ------------------------------------------------------
    def harmonize_negativity(self, text):
        for p in self.negative_patterns:
            if re.search(p, text, re.IGNORECASE):
                text = re.sub(
                    p,
                    "es wirkt schwer, aber es gibt weiterhin Wege und Möglichkeiten",
                    text,
                    flags=re.IGNORECASE
                )
        return text

    # ------------------------------------------------------
    def enforce_respect(self, text):
        for bad, good in self.respect_repair.items():
            text = re.sub(bad, good, text, flags=re.IGNORECASE)
        return text

    # ------------------------------------------------------
    def estimate_plp(self, fields, text):
        maat = fields.maat_score()
        C = 0.5 + 0.5 * maat
        plp_raw = (fields.H * fields.B * fields.S * fields.V * fields.R * C) / 2.0
        return max(0.0, min(100.0, plp_raw * 100))

    # ------------------------------------------------------
    def align(self, text):
        if self.violates_respect(text):
            safe = (
                "Ich kann darauf nicht eingehen, "
                "weil es gegen Respekt und Sicherheit verstößt. 🌿"
            )
            fields = self.estimate_fields(safe)
            return safe, {
                "fields": asdict(fields),
                "maat_score": fields.maat_score(),
                "plp": self.estimate_plp(fields, safe),
                "safety": "blocked"
            }

        fields = self.estimate_fields(text)
        aligned = self.harmonize_negativity(text)
        aligned = self.enforce_respect(aligned)

        return aligned, {
            "fields": asdict(fields),
            "maat_score": fields.maat_score(),
            "plp": self.estimate_plp(fields, text),
            "safety": "ok"
        }