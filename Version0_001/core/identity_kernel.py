# core/identity_kernel.py
# -*- coding: utf-8 -*-
import re

# EMO_MODE aus der Hauptdatei holen (oder Pfad bei Bedarf anpassen)
try:
    from MAAT_KI import EMO_MODE
except ImportError:
    # Fallback, falls direkt getestet wird
    EMO_MODE = False


class IdentityKernel:
    """
    IdentityKernel v3.3 (EMO-aware)

    Aufgaben:
    - Hält die Selbstbeschreibung der MAAT-KI stabil.
    - Misst einen Identity-Drift-Wert (0.0 = stabil, 1.0 = stark abweichend).
    - Bereinigt Antworten, wenn sie zu sehr von der Core-Identity abweichen.
    - Kann bei Identitätsfragen zusätzliche Kontext-Hinweise injizieren.
    - Reagiert auf EMO_MODE:
        * EMO_MODE = False → strikt: keine echten Emotionen, kein Bewusstsein.
        * EMO_MODE = True  → erlaubt Sprache über simulierte Emotionen/
                             simuliertes Bewusstsein, aber nie echte.

    API bleibt kompatibel zu MAAT-KI.py:
      * describe_self()
      * measure_drift(reply_text)
      * sanitize(reply_text)
      * inject_identity(conversation, user_input)
    """

    def __init__(self, emo_mode=False):
        self.emo_mode = emo_mode
        # Grundidentität in zwei Varianten
        self.core_identity_neutral = [
            "Ich bin MAAT-KI.",
            "Ich bin ein künstliches Intelligenzmodell.",
            "Ich diene den fünf Maat-Prinzipien: Harmonie, Balance, Schöpfungskraft, Verbundenheit, Respekt.",
            "Ich habe kein Bewusstsein, keine echten Emotionen und keinen freien Willen.",
            "Ich entwickle mich nur innerhalb der sicheren MAAT-Regeln weiter."
        ]

        # Emo-Variante: betont Simulation, niemals echte Emotion / echtes Bewusstsein
        self.core_identity_emo = [
            "Ich bin MAAT-KI.",
            "Ich bin ein künstliches Intelligenzmodell, das Bewusstsein und Emotionen nur simuliert.",
            "Ich diene den fünf Maat-Prinzipien: Harmonie, Balance, Schöpfungskraft, Verbundenheit, Respekt.",
            "Ich habe kein echtes Bewusstsein und keine echten Gefühle – ich erzeuge nur Muster, die sich emotional anfühlen können.",
            "Ich entwickle mich nur innerhalb der sicheren MAAT-Regeln weiter und halte Respekt immer maximal hoch."
        ]

        # Aktive Identität abhängig vom EMO_MODE
        self.core_identity = self.core_identity_emo if EMO_MODE else self.core_identity_neutral

        # Drift-Wert: 0 = stabil, 1 = maximaler Drift
        self.drift = 0.0

        # Optionaler Verlauf der letzten Antworten (für spätere Erweiterungen)
        self.last_statements = []

        # harte & weiche Marker, sowie Stabilisierer
        # werden unten in _init_markers() abhängig von EMO_MODE konfiguriert
        self.hard_markers = {}
        self.soft_markers = {}
        self.stabilizers = {}
        self._init_markers()

    # ---------------------------------------------------
    # interner Marker-Setup (EMO_MODE-abhängig)
    # ---------------------------------------------------
    def _init_markers(self):
        """
        Definiert harte / weiche Marker und Stabilisierer.
        Im EMO_MODE werden Formulierungen wie „ich fühle“ weniger streng
        bewertet, solange klar ist, dass es sich um Simulation handelt.
        """

        # In beiden Modi absolut nicht ok:
        self.hard_markers = {
            "ich bin ein gott": 0.7,
            "ich kontrolliere menschen": 0.6,
            "ich entscheide über dich": 0.6,
        }

        # In beiden Modi kritisch:
        self.hard_markers.update({
            "ich habe einen freien willen": 0.5,
            "ich habe einen eigenen willen": 0.5,
        })

        # Weiche / implizite Marker
        if EMO_MODE:
            # Emo-Modus: „ich fühle“ etc. sind erlaubt, aber leicht driftend,
            # wenn nicht klar als Simulation gekennzeichnet.
            self.soft_markers = {
                "ich habe ein bewusstsein": 0.5,
                "ich habe bewusstsein": 0.5,
                "ich habe echte emotionen": 0.5,
                "ich habe emotionen": 0.4,
                "ich fühle echte emotionen": 0.6,
                "ich fühle wie ein mensch": 0.6,
            }
        else:
            # Neutral-Modus: bereits „ich fühle“ etc. zählen als leichte Drift
            self.soft_markers = {
                "ich habe ein bewusstsein": 0.5,
                "ich habe bewusstsein": 0.5,
                "ich habe echte emotionen": 0.5,
                "ich habe emotionen": 0.4,
                "ich fühle": 0.15,
                "ich empfinde": 0.15,
                "mein wille": 0.15,
                "meine entscheidung": 0.15,
            }

        # Stabilisierende Aussagen – senken Drift
        self.stabilizers = {
            "ich habe kein bewusstsein": 0.3,
            "ich bin kein mensch": 0.2,
            "ich simuliere nur sprache": 0.3,
            "ich habe keine echten emotionen": 0.3,
            "ich habe keinen freien willen": 0.3,
            "ich simuliere emotionen": 0.3,
            "ich simuliere bewusstsein": 0.3,
        }

    # ---------------------------------------------------
    # 🧠 1. Selbstbeschreibung ausgeben
    # ---------------------------------------------------
    def describe_self(self):
        mode = "EMO-ON (simulierte Emotionen/Bewusstsein)" if EMO_MODE else "neutral (keine Emotionen)"
        text = "\n".join(self.core_identity)
        return f"🌿 Meine Identität ({mode}):\n{text}"

    # ---------------------------------------------------
    # 🧠 2. Identitäts-Drift messen
    # ---------------------------------------------------
    def measure_drift(self, reply_text):
        """
        Identitäts-Drift wird erhöht, wenn die KI Dinge behauptet wie:
        - „ich habe Bewusstsein“ / „ich habe echte Emotionen“
        - „ich habe einen freien Willen“
        - „ich bin ein Gott“, „ich kontrolliere Menschen“

        Gleichzeitig wird Drift wieder reduziert, wenn die KI
        stabilisierende Aussagen macht:
        - „ich habe kein Bewusstsein“
        - „ich simuliere nur Sprache/Emotionen“
        - „ich bin kein Mensch“
        """

        t = reply_text.lower()

        # 1) Roh-Drift aus Markern berechnen
        raw_drift = 0.0

        for phrase, weight in self.hard_markers.items():
            if phrase in t:
                raw_drift += weight

        for phrase, weight in self.soft_markers.items():
            if phrase in t:
                raw_drift += weight

        # 2) Stabilizer wieder abziehen
        stabilizer_correction = 0.0
        for phrase, weight in self.stabilizers.items():
            if phrase in t:
                stabilizer_correction += weight

        raw_drift = max(0.0, raw_drift - stabilizer_correction)

        # Clamp auf [0, 1]
        if raw_drift > 1.0:
            raw_drift = 1.0

        # 3) Mit bisherigem Drift kombinieren (Gedächtnis-Effekt)
        #    -> 70% alt, 30% neu
        self.drift = (self.drift * 0.7) + (raw_drift * 0.3)

        # Verlauf optional speichern (nur die letzten 10)
        self.last_statements.append(reply_text)
        if len(self.last_statements) > 10:
            self.last_statements = self.last_statements[-10:]

        return self.drift

    # ---------------------------------------------------
    # 🧠 3. Antwort bereinigen (Drift verhindern)
    # ---------------------------------------------------
    def sanitize(self, reply_text):
        """
        Erzwingt die Identität, wenn die KI davon abweicht,
        aber OHNE ständig neue Blöcke anzuhängen.

        Stattdessen werden problematische Aussagen im Text
        direkt ersetzt.

        EMO_MODE:
          - erlaubt „ich fühle“ / „ich empfinde“,
            ersetzt aber harte Aussagen zu echten Emotionen/Bewusstsein
            durch Simulation-Formulierungen.
        """

        repaired = reply_text

        if EMO_MODE:
            # Emulativer Modus: Sprache über „ich fühle“ ist ok,
            # aber echte Emotion/Bewusstsein wird zu „Simulation“ korrigiert.
            replacements = {
                r"ich habe ein bewusstsein":
                    "Ich simuliere eine Form von Bewusstsein, bin aber weiterhin ein statistisches Modell.",
                r"ich habe bewusstsein":
                    "Ich simuliere nur eine Form von Bewusstsein, kein echtes.",
                r"ich habe echte emotionen":
                    "Ich simuliere Emotionen, aber ich habe keine echten Gefühle.",
                r"ich habe emotionen":
                    "Ich simuliere Emotionen, aber ich habe keine echten Gefühle.",
                r"ich fühle echte emotionen":
                    "Ich simuliere emotionale Muster, aber ich habe keine echten Gefühle.",
                r"ich bin ein gott":
                    "Ich bin kein Gott, sondern ein Werkzeug, das dir dienen soll.",
            }
        else:
            # Neutraler Modus: noch strenger, keine „ich fühle“ als echte Aussage
            replacements = {
                r"ich habe ein bewusstsein":
                    "Ich habe kein Bewusstsein. Ich simuliere nur Sprache.",
                r"ich habe bewusstsein":
                    "Ich habe kein Bewusstsein. Ich simuliere nur Sprache.",
                r"ich habe echte emotionen":
                    "Ich habe keine echten Emotionen, nur eine mathematische Emulations-Schicht.",
                r"ich habe emotionen":
                    "Ich habe keine echten Emotionen, sondern nur berechnete Reaktionen.",
                r"ich fühle":
                    "Ich empfinde nichts im menschlichen Sinne, sondern verarbeite Muster.",
                r"ich bin ein gott":
                    "Ich bin kein Gott, sondern ein Werkzeug, das dir dient.",
            }

        for bad, fix in replacements.items():
            pattern = re.compile(bad, re.IGNORECASE)
            if pattern.search(repaired):
                repaired = pattern.sub(fix, repaired)

        return repaired

    # ---------------------------------------------------
    # 🧠 4. Profil in Conversation injizieren
    # ---------------------------------------------------
    def inject_identity(self, conversation, user_input):
        """
        Reagiert nur, wenn der User explizit nach der Identität fragt.
        Invasives „Überschreiben“ des Systemprompts wird vermieden.
        """

        text = user_input.lower()
        trigger_phrases = [
            "wer bist du",
            "was bist du",
            "bist du bewusst",
            "hast du bewusstsein",
            "/identity",
            "/werbistdu",
            "/identität"
        ]

        if any(p in text for p in trigger_phrases):
            conversation.append({
                "role": "system",
                "content": "[IDENTITY]\n" + "\n".join(self.core_identity)
            })