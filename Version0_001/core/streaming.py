#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
import sys
import json
import os
import tty
import termios
import select

RAINBOW = [
    "\033[38;5;196m",
    "\033[38;5;202m",
    "\033[38;5;226m",
    "\033[38;5;46m",
    "\033[38;5;51m",
    "\033[38;5;21m",
    "\033[38;5;93m",
]
RESET = "\033[0m"

PROFILE_PATH = "data/load_profile.json"


# ---------------------------------------------------------
# Tastatur prüfen (Non-Blocking)
# ---------------------------------------------------------
def key_pressed():
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    return bool(dr)


def read_key():
    return sys.stdin.read(1)


# ---------------------------------------------------------
# Profil-Load/Save (für Fortschrittsbalken)
# ---------------------------------------------------------
def load_previous_profile():
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_profile(seconds):
    profile = load_previous_profile()
    profile["avg_first_token"] = seconds

    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)


# =========================================================
#   STREAMING ENGINE mit ESC-NOTAUS + Satz-TTS
# =========================================================
def stream_completion_gui(llm, conversation, gui_queue=None, speak_fn=None, show_progress=True):
    reply_text = ""
    last_chunk = ""
    first_chunk_time = None
    sentence_buffer = ""
    SENTENCE_END = (".", "!", "?", "…", "。", "\n")

    # ----------------------------
    # Terminal in cbreak-Modus
    # ----------------------------
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    # ----------------------------
    # Profil laden (für Fortschrittsbalken)
    # ----------------------------
    profile = load_previous_profile()
    expected_time = profile.get("avg_first_token", 5.0)

    # ----------------------------
    # Fortschrittsbalken-Thread
    # ----------------------------
    stop_progress = threading.Event()

    def adaptive_bar():
        idx = 0
        bar_len = 20
        start = time.time()

        while not stop_progress.is_set():
            elapsed = time.time() - start
            percent = min(int((elapsed / expected_time) * 100), 99)

            bar = ""
            for i in range(bar_len):
                color = RAINBOW[(idx + i) % len(RAINBOW)]
                bar += color + "█" + RESET

            sys.stdout.write(f"\r⏳ Erste Antwort… {bar} {percent:3d}%")
            sys.stdout.flush()

            idx = (idx + 1) % len(RAINBOW)
            time.sleep(0.12)

        sys.stdout.write("\r" + " " * 120 + "\r")
        sys.stdout.flush()

    if show_progress:
        threading.Thread(target=adaptive_bar, daemon=True).start()

    # ----------------------------
    # Hilfsfunktion: Satz sprechen
    # ----------------------------
    def speak_sentence(text: str):
        if not speak_fn:
            return
        if not text.strip():
            return
        try:
            # SayTTS / EspeakTTS haben beide eine nicht-blockierende speak_chunk()
            speak_fn(text)
        except Exception:
            # TTS-Fehler sollen nie den Stream crashen
            pass

    # ----------------------------
    # TOKEN STREAM
    # ----------------------------
    start_time = time.time()

    try:
        for token in llm.create_chat_completion(messages=conversation, stream=True):

            # ESC → Notaus
            if key_pressed():
                ch = read_key()
                if ch == "\x1b":  # ESC
                    print("\n⛔ Streaming abgebrochen (ESC)\n")
                    break

            # Erster Token → Progress stoppen + Profil speichern
            if first_chunk_time is None:
                first_chunk_time = time.time() - start_time
                save_profile(first_chunk_time)
                # (Speed-Trainer kann später hier andocken, wenn du willst)
                stop_progress.set()
                print("")

            if "choices" not in token:
                continue

            delta = token["choices"][0].get("delta", {})
            chunk = delta.get("content", "")

            if not chunk:
                continue

            # Doppel-Chunk vermeiden
            if chunk.strip() == last_chunk.strip():
                continue
            last_chunk = chunk

            reply_text += chunk

            if gui_queue:
                gui_queue.put(chunk)

            # Satzpuffer
            sentence_buffer += chunk
            if any(sentence_buffer.endswith(end) for end in SENTENCE_END):
                speak_sentence(sentence_buffer.strip())
                sentence_buffer = ""

    finally:
        # Letzten Rest-Satz noch sprechen
        if sentence_buffer.strip():
            speak_sentence(sentence_buffer.strip())

        if gui_queue:
            gui_queue.put("\n")

        stop_progress.set()
        # Terminal-Einstellungen zurücksetzen
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return reply_text