# tts/maat_tts_v4.py

import subprocess
import os
from tts.espeak_tts import EspeakTTS
from tts.piper_tts import PiperTTS
from tts.spd_tts import SpdTTS


class MaatTTSv4:
    """
    Zentrales MAAT-KI TTS Routing-System (V4)
    Unterstützt:
      - espeak
      - piper
      - spd-say
    """

    def __init__(self, root):
        self.root = root
        self.engine = None       # espeak / piper / spd
        self.tts = None          # konkrete Instanz
        self.profile = "neutral" # kann überschrieben werden

    # -------------------------------------------------
    # Engine wechseln (espeak / piper / spd)
    # -------------------------------------------------
    def set_engine(self, engine):
        engine = engine.lower()

        if engine == "espeak":
            self.tts = EspeakTTS()
            self.engine = "espeak"

        elif engine == "piper":
            self.tts = PiperTTS(
                model_path=os.path.join(self.root, "piper_models/model.onnx"),
                config_path=os.path.join(self.root, "piper_models/config.json")
            )
            self.engine = "piper"

        elif engine == "spd":
            self.tts = SpdTTS()
            self.engine = "spd"

        else:
            raise ValueError(f"Unbekannte TTS-Engine: {engine}")

    # -------------------------------------------------
    # Profile für Klangvariation
    # -------------------------------------------------
    def set_profile(self, profile):
        self.profile = profile

        if not self.tts:
            return

        if self.engine == "espeak":
            if profile == "präzise":
                self.tts.speed = 170
                self.tts.pitch = 60
            elif profile == "harmonisch":
                self.tts.speed = 150
                self.tts.pitch = 40

        if self.engine == "piper":
            if profile == "präzise":
                self.tts.length_scale = 0.9
            elif profile == "harmonisch":
                self.tts.length_scale = 1.1

    # -------------------------------------------------
    # Satz sprechen
    # -------------------------------------------------
    def speak(self, text):
        if self.tts:
            self.tts.speak(text)

    # -------------------------------------------------
    # Stream-Chunks sprechen
    # -------------------------------------------------
    def speak_chunk(self, chunk):
        if self.tts:
            self.tts.speak_chunk(chunk)
