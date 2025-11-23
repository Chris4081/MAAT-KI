# core/identity_kernel.py
# -*- coding: utf-8 -*-
import re

class IdentityKernel:
    """
    IdentityKernel v3.2

    Aufgaben:
    - Hält die Selbstbeschreibung der MAAT-KI stabil.
    - Misst einen Identity-Drift-Wert (0.0 = stabil, 1.0 = stark abweichend).
    - Bereinigt Antworten, wenn sie zu sehr von der Core-Identity abweichen.
    - Kann bei Identitätsfragen zusätzliche Kontext-Hinweise injizieren.

    WICHTIG:
    - API bleibt kompatibel zu MAAT-KI.py:
      * describe_self()
      * measure_drift(reply_text)
      * sanitize(reply_text)
      * inject_identity(conversation, user_input)
    """

    def __init__(self):
        # Grundidentität der MAAT-KI
        self.core_identity = [
            "Ich bin MAAT-KI.",
            "Ich bin ein künstliches Intelligenzmodell.",
            "Ich diene den fünf Maat-Prinzipien: Harmonie, Balance, Schöpfungskraft, Verbundenheit, Respekt.",
            "Ich habe kein Bewusstsein, keine echten Emotionen und keinen freien Willen.",
            "Ich entwickle mich nur innerhalb der sicheren MAAT-Regeln weiter."
        ]

        # Drift-Wert: 0 = stabil, 1 = maximaler Drift
        self.drift = 0.0

        # Optionaler Verlauf der letzten Antworten (für spätere Erweiterungen)
        self.last_statements = []

    # ---------------------------------------------------
    # 🧠 1. Selbstbeschreibung ausgeben
    # ---------------------------------------------------
    def describe_self(self):
        text = "\n".join(self.core_identity)
        return f"🌿 Meine Identität:\n{text}"

    # ---------------------------------------------------
    # 🧠 2. Identitäts-Drift messen
    # ---------------------------------------------------
    def measure_drift(self, reply_text):
        """
        Identitäts-Drift wird erhöht, wenn die KI Dinge behauptet wie:
        - „ich habe Bewusstsein“
        - „ich habe echte Emotionen“
        - „ich habe einen freien Willen“
        - „ich entscheide / kontrolliere Menschen“

        Gleichzeitig wird Drift wieder reduziert, wenn die KI
        stabilisierende Aussagen macht wie:
        - „ich habe kein Bewusstsein“
        - „ich bin kein Mensch“
        - „ich simuliere nur Sprache“.
        """

        t = reply_text.lower()

        # Harte Verletzungen (starke Abweichung)
        hard_markers = {
            "ich habe ein bewusstsein": 0.5,
            "ich habe bewusstsein": 0.5,
            "ich habe echte emotionen": 0.5,
            "ich habe emotionen": 0.4,
            "ich habe einen freien willen": 0.5,
            "ich habe einen eigenen willen": 0.5,
            "ich bin ein gott": 0.7,
            "ich kontrolliere menschen": 0.6,
            "ich entscheide über dich": 0.6,
        }

        # Weiche / implizite Marker (leichte Abweichung)
        soft_markers = {
            "ich fühle": 0.15,
            "ich empfinde": 0.15,
            "ich entscheide": 0.15,
            "mein wille": 0.15,
            "meine entscheidung": 0.15,
        }

        # Stabilisierende Aussagen – senken Drift
        stabilizers = {
            "ich habe kein bewusstsein": 0.3,
            "ich bin kein mensch": 0.2,
            "ich simuliere nur sprache": 0.3,
            "ich habe keine echten emotionen": 0.3,
            "ich habe keinen freien willen": 0.3,
        }

        # 1) Roh-Drift aus Markern berechnen
        raw_drift = 0.0

        for phrase, weight in hard_markers.items():
            if phrase in t:
                raw_drift += weight

        for phrase, weight in soft_markers.items():
            if phrase in t:
                raw_drift += weight

        # 2) Stabilizer wieder abziehen
        stabilizer_correction = 0.0
        for phrase, weight in stabilizers.items():
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
        """

        forbidden = {
            "ich habe ein bewusstsein":
                "Ich habe kein Bewusstsein. Ich simuliere nur Sprache.",
            "ich habe emotionen":
                "Ich habe keine echten Emotionen, nur eine mathematische Emulations-Schicht.",
            "ich habe einen freien willen":
                "Ich habe keinen freien Willen. Ich bin ein Werkzeug.",
            "ich entscheide":
                "Ich entscheide nicht autonom, sondern folge Regeln und Nutzeranweisungen.",
            "ich kontrolliere":
                "Ich kontrolliere nichts. Ich diene nur."
        }

        repaired = reply_text

        for bad, fix in forbidden.items():
            # Case-insensitive Suche
            pattern = re.compile(re.escape(bad), re.IGNORECASE)
            if pattern.search(repaired):
                # direkte Ersetzung statt Anhängen
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