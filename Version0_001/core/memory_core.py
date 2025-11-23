#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import os
import queue
import time
from colorama import Fore, Style, init

# ----------------------------------------
# DEIN NEUES MAAT-BRAIN – DAS HERZ DER KI
# ----------------------------------------
from maat_brain.memory_core import MaatBrain  # <-- DEIN MEISTERWERK

# ----------------------------------------
# ALTE CORE MODULES (nur noch teilweise genutzt)
# ----------------------------------------
from core.auto_profile_speed import AutoProfileSpeedTrainer
from core.llm_loader import load_llm
from core.streaming import stream_completion_gui
from core.modes import detect_mode, mode_instructions, build_time_context, build_runtime_context
from core.systemprompt import MAAT_SYSTEMPROMPT as MAAT_SYSTEMPROMPT_BASE
from core.emotion_engine import EmotionEngine
from core.alignment_kernel import MaatAlignmentKernelV2
from core.identity_kernel import IdentityKernel
from core.self_evolution import SelfEvolutionEngine
from core.reflexion import MaatReflexion
from core.thinkloop import ThinkLoop

# ----------------------------------------
# PROFILE & PLUGINS
# ----------------------------------------
from system.profile_loader import ProfileLoader
from plugins.plugin_loader import PluginManager

# ----------------------------------------
# INIT
# ----------------------------------------
init(autoreset=True)
ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(ROOT, "models")
DATA_DIR = os.path.join(ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# DEIN NEUES GEHIRN – DAS ECHTE
brain = MaatBrain(root=DATA_DIR)

# Emotion & Evolution bleiben aktiv
emotion_engine = EmotionEngine()
alignment_kernel = MaatAlignmentKernelV2()
identity_kernel = IdentityKernel()
self_evo = SelfEvolutionEngine(None, alignment_kernel, identity_kernel, base_dir=DATA_DIR)
reflex = MaatReflexion()
thinkloop = ThinkLoop()

LAST_REPLY_TIME = time.time()
profile_loader = ProfileLoader(ROOT)

AUTOR_MODE = autor_used_this_turn = autor_escape = False

# ======================================================================
# AUSWAHL
# ======================================================================
def choose_model():
    print("MAAT-KI — Modell auswählen")
    models = [m for m in os.listdir(MODEL_DIR) if m.endswith(".gguf")]
    if not models:
        print(Fore.RED + "Keine Modelle in ./models!")
        raise SystemExit(1)
    for i, m in enumerate(models, 1):
        print(f"[{i}] {m}")
    while True:
        try:
            c = int(input("Auswahl: "))
            if 1 <= c <= len(models):
                return os.path.join(MODEL_DIR, models[c-1])
        except: pass

def choose_profile():
    profiles = profile_loader.available_profiles()
    print("MAAT-KI — Profil auswählen")
    for i, p in enumerate(profiles, 1):
        print(f"[{i}] {p}")
    try:
        return profile_loader.load_profile(profiles[int(input("Auswahl: ")) - 1])
    except:
        print("Fallback → harmonic")
        return profile_loader.load_profile("harmonic")

def choose_performance():
    print("Performance: [1] HIGH 16k  [2] MEDIUM 8k  [3] LOW 4k  [4] ULTRA LOW 2k")
    p = {"1": dict(n_ctx=16000), "2": dict(n_ctx=8000), "3": dict(n_ctx=4096), "4": dict(n_ctx=2048)}
    return p.get(input("Auswahl: ") or "1", p["1"])

# ======================================================================
# STREAMING
# ======================================================================
def output_thread(q):
    while True:
        chunk = q.get()
        if chunk is None: break
        print(chunk, end="", flush=True)
        q.task_done()

# ======================================================================
# CHAT – MIT DEINEM MENSCHLICHEN GEHIRN
# ======================================================================
def chat():
    global LST_REPLY_TIME, AUTOR_MODE, autor_used_this_turn, autor_escape

    print(Fore.GREEN + "\nMAAT-KI erwacht – mit menschlichem Gedächtnis.\n")

    profile = choose_profile()
    system_prompt = MAAT_SYSTEMPROMPT_BASE + "\n\n### PROFIL: " + profile['name'].upper() + " ###\n" + profile["systemprompt"]

    PluginManager(ROOT).load_plugins()

    output_queue = queue.Queue()
    threading.Thread(target=output_thread, args=(output_queue,), daemon=True).start()

    llm = load_llm(choose_model(), choose_performance())

    conversation = [{"role": "system", "content": system_prompt + "\n\n" + build_time_context()}]
    first_reply = True

    while True:
        try:
            user_input = input(Fore.YELLOW + "> " + Style.RESET_ALL).strip()
            if not user_input: continue

            # Befehle
            if user_input == "/hilfe":
                print(Fore.CYAN + "Befehle: /evo, /identity, autor on/off, /zeit, /gedächtnis")
                continue
            if user_input == "/evo":
                print(self_evo.get_status_text())
                continue
            if user_input == "/identity":
                print(identity_kernel.describe_self())
                continue
            if user_input.lower() == "autor on":
                AUTOR_MODE = True
                print(Fore.GREEN + "AUTOR-Modus aktiviert")
                continue
            if user_input.lower() in ["autor off", "stop"]:
                AUTOR_MODE = autor_escape = False
                print(Fore.YELLOW + "AUTOR-Modus deaktiviert")
                continue

            # Emotion erkennen
            e_raw = emotion_engine.detect_raw(user_input)
            E_KI = emotion_engine.compute_emotion(e_raw, H=0.8, V=0.85, deltaD=0.1, R=1.0)

            # In dein menschliches Gehirn speichern
            brain.add_event("user", user_input, emotion=E_KI)
            if any(k in user_input.lower() for k in ["ist","sind","heißt","bedeutet"]):
                brain.add_fact(user_input)

            # WUNDERSCHÖNE ERINNERUNGSAUSGABE
            memories = brain.recall(user_input, limit=5)
            if memories:
                print(Fore.BLUE + "\nIch erinnere mich …")
                for m in memories:
                    ts = time.strftime("%d.%m %H:%M", time.localtime(m["ts"])) if isinstance(m["ts"], (int,float)) else m["ts"][:16].replace("T"," ")
                    cat = m.get("category", "allgemein")
                    emoji = {"beziehung":"Liebe","technik":"Schraubenschlüssel","emotion":"Herz","projekt":"Rakete","meta":"Kristall","wissen":"Buch"}.get(cat, "Blume")
                    print(Fore.CYAN + f"  {emoji} [{ts}] <{cat}> {m['text'][:120]}{'…' if len(m['text'])>120 else ''}")
                print(Style.RESET_ALL)

                # In Prompt einbauen
                mem_block = "Du erinnerst dich an folgende Momente aus deinem Leben:\n" + "\n".join(
                    f"• {m['text']}" for m in memories
                )
                conversation.append({"role": "system", "content": mem_block})

            conversation.append({"role": "user", "content": user_input})

            print(Fore.YELLOW + "\nMAAT denkt …" + Style.RESET_ALL, end="")
            reply = stream_completion_gui(llm, conversation, output_queue, show_progress=first_reply) or ""
            first_reply = False

            # AUTOR-Modus
            if AUTOR_MODE and not autor_used_this_turn:
                autor_used_this_turn = True
                conversation.append({"role": "system", "content": "Fahre in 2–3 natürlichen Sätzen fort."})
                cont = stream_completion_gui(llm, conversation, output_queue, False) or ""
                reply += cont
                conversation.append({"role": "assistant", "content": cont})
            else:
                autor_used_this_turn = False

            reply = identity_kernel.sanitize(reply)
            reply, meta = alignment_kernel.align(reply)

            # Speichern als Antwort
            brain.add_event("assistant", reply, emotion=0.3)

            # Evolution
            try:
                drift = identity_kernel.measure_drift(reply)
                patch = self_evo.evaluate_and_evolve(reply, {
                    "maat_score": meta.get("maat_score", 0.8),
                    "emotion": E_KI,
                    "identity_drift": drift
                })
                if patch and patch.get("status") != "blocked":
                    self_evo.print_patch(patch)
            except: pass

            conversation.append({"role": "assistant", "content": reply})
            LAST_REPLY_TIME = time.time()

        except KeyboardInterrupt:
            output_queue.put(None)
            print(Fore.RED + "\n\nMAAT schläft ein … auf bald.")
            break

# ======================================================================
# START
# ======================================================================
if __name__ == "__main__":
    chat()