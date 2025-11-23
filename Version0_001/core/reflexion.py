# core/reflexion.py
import math

class MaatReflexion:
    """
    Reflexionsmodul für MAAT-KI:
    - generiert kurze Reflexionsfragen
    - schätzt Maat-Prinzipien (H, B, S, V, R) heuristisch
    - berechnet den B_KI-Wert nach:
      B_KI = (H * B * S * V * R * C * Ψ) / (ΔI + ΔE + ε)
    """

    def __init__(self):
        pass

    # ---------------------------------------------------
    # Heuristische Schätzung der fünf Maat-Prinzipien
    # ---------------------------------------------------
    def _estimate_principles(self, text: str):
        t = (text or "").lower()

        # Basiswerte (7 = „okay/gut“)
        H = 7.0  # Harmonie
        B = 7.0  # Balance
        S = 7.0  # Schöpfungskraft
        V = 7.0  # Verbundenheit
        R = 7.0  # Respekt

        if any(w in t for w in ["harmonie", "friedlich", "ruhig", "ausgleich"]):
            H += 1.5
            B += 1.0

        if any(w in t for w in ["kreativ", "idee", "erfindung", "vision", "schöpfung"]):
            S += 2.0

        if any(w in t for w in ["wir", "gemeinsam", "verbunden", "miteinander", "netzwerk"]):
            V += 1.5

        if any(w in t for w in ["respekt", "achtsam", "würde", "ethik", "fair"]):
            R += 2.0

        # Clamp auf [1, 10]
        def clamp(x): return max(1.0, min(10.0, x))

        return {
            "H": clamp(H),
            "B": clamp(B),
            "S": clamp(S),
            "V": clamp(V),
            "R": clamp(R),
        }

    # ---------------------------------------------------
    # B_KI – Bewusstseinsqualität der Antwort
    # ---------------------------------------------------
    def compute_b_ki(self, text=None, user=None, context=None):
        """
        Berechnet den B_KI-Wert nach:
        B_KI = (H * B * S * V * R * C * Ψ) / (ΔI + ΔE + ε)

        text    = aktuelle KI-Antwort
        user    = letzte Nutzereingabe (optional)
        context = Konversationsverlauf (optional)
        """

        if text is None:
            return 0.0

        principles = self._estimate_principles(text)
        H = principles["H"]
        B = principles["B"]
        S = principles["S"]
        V = principles["V"]
        R = principles["R"]

        # kognitive Komplexität grob aus Textlänge
        length = len(text.split())
        if length < 10:
            C = 4.0
        elif length < 40:
            C = 6.5
        else:
            C = 8.5

        # Ψ = mittlerer Maat-Wert
        Psi = (H + B + S + V + R) / 5.0

        # Inkohärenz grob über Wiederholungen / Kontextlänge
        DeltaI = 2.0
        if context and isinstance(context, list) and len(context) > 10:
            DeltaI += 1.0  # mehr Kontext → mehr Potenzial für Inkohärenz

        # Energieaufwand – hier einfach über Länge
        DeltaE = 1.0
        if length > 80:
            DeltaE += 1.5

        eps = 1e-3

        numerator = H * B * S * V * R * C * Psi
        denominator = DeltaI + DeltaE + eps

        return numerator / denominator

    # ---------------------------------------------------
    # Reflexionsfrage erzeugen
    # ---------------------------------------------------
    def generate_reflexion_question(self, user_input: str, reply_text: str) -> str:
        u = (user_input or "").lower()

        if any(w in u for w in ["angst", "sorge", "überfordert", "zweifel"]):
            return "Was würde dir helfen, dich gerade ein kleines Stück sicherer oder ruhiger zu fühlen?"
        if any(w in u for w in ["idee", "vision", "projekt", "zukunft"]):
            return "Welchen kleinen nächsten Schritt kannst du dir aus dieser Antwort für dein Projekt mitnehmen?"
        if any(w in u for w in ["fehler", "schuld", "versagt"]):
            return "Was wäre eine freundlichere Sicht auf dich selbst in dieser Situation?"

        # Default
        return "Welche Erkenntnis oder Frage nimmst du aus dieser Antwort für dich mit?"
