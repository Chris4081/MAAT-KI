import subprocess
import threading
import queue
import time
import os


class EspeakTTS:
    def __init__(self, voice="de", speed=165):
        self.voice = voice
        self.speed = speed

        self.buffer = ""           # Satzpuffer
        self.sentence_end = (".", "!", "?", "…")

        # Queue für Sätze, die gelesen werden sollen
        self.speak_queue = queue.Queue()

        # Hintergrund-Thread starten
        self.worker = threading.Thread(target=self._speak_worker, daemon=True)
        self.worker.start()

    # --------------------------------------------------------
    # WORKER: Liest nacheinander, niemals zwei gleichzeitig!
    # --------------------------------------------------------
    def _speak_worker(self):
        while True:
            sentence = self.speak_queue.get()
            if not sentence.strip():
                continue

            cmd = [
                "espeak",
                "-v", self.voice,
                "-s", str(self.speed),
                sentence
            ]

            # Prozess läuft blockierend → kein Overlap
            subprocess.call(cmd)

            time.sleep(0.05)

    # --------------------------------------------------------
    # STREAMING-CHUNK VERARBEITEN
    # --------------------------------------------------------
    def speak_chunk(self, chunk):
        self.buffer += chunk

        # wenn Satzende → abspielen
        if any(self.buffer.endswith(end) for end in self.sentence_end):
            text = self.buffer.strip()
            self.buffer = ""
            self.speak_queue.put(text)

    # --------------------------------------------------------
    # Restliches flushen
    # --------------------------------------------------------
    def finish(self):
        if self.buffer.strip():
            self.speak_queue.put(self.buffer.strip())
            self.buffer = ""


