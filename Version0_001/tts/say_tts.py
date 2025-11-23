#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import subprocess
import queue
import platform
import time


class SayTTS:
    """
    Einfache TTS-Engine für macOS über 'say'.
    Nutzt eine Queue + Worker-Thread, damit Aufrufe nicht blockieren.
    """

    def __init__(self, voice=None, rate=180):
        self.voice = voice
        self.rate = rate
        self._queue = queue.Queue()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _build_cmd(self, text: str):
        cmd = ["say"]
        if self.voice:
            cmd += ["-v", self.voice]
        if self.rate:
            cmd += ["-r", str(self.rate)]
        cmd.append(text)
        return cmd

    def _run(self):
        system = platform.system().lower()
        if system != "darwin":
            # Auf Nicht-macOS einfach still bleiben
            return

        while not self._stop.is_set():
            try:
                text = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if text is None:
                break

            try:
                cmd = self._build_cmd(text)
                subprocess.run(cmd)
            except Exception:
                # Audio-Fehler nicht weiterwerfen
                pass

            time.sleep(0.01)

    def speak(self, text: str):
        """Öffentliche Methode: Text in die Warteschlange legen."""
        if not text:
            return
        self._queue.put(text)

    def speak_chunk(self, text: str):
        """Kompatibel zu EspeakTTS.speak_chunk – wird von streaming.py genutzt."""
        self.speak(text)

    def close(self):
        """Thread sauber stoppen."""
        self._stop.set()
        self._queue.put(None)