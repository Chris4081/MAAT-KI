#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import os
import queue
import time
from colorama import Fore, Style, init

# ----------------------------------------
# CORE MODULES
# ----------------------------------------
from core.persona_engine import PersonaEngine
from system.help_text import HELP_TEXT
from system.gameinfo import show_game_info
from core.auto_profile_speed import AutoProfileSpeedTrainer
from core.long_term_memory import LongTermMemory
from core.semantic_memory import SemanticMemory
from core.episodic_memory import EpisodicMemory
from core.brain_memory import BrainMemory
from core.memory_narrative import MemoryNarrative
from core.memory_fusion import MemoryFusion
from core.context_anchor import ContextAnchor
from core.memory_backup import MemoryBackup
from system.guide_text import GUIDE_TEXT
from core.quest_engine import QuestEngine
from core.llm_loader import load_llm
from core.emotion_maat_mapper import EmotionMaatMapper
from core.memory_sqlite import SQLiteMemory
from core.mie import MaatIntuitionEngine
from core.reflexion import MaatReflexion
from core.emo_mode_switch import select_emo_mode
EMO_MODE = select_emo_mode()
from core.self_evolution import SelfEvolutionEngine
from core.streaming import stream_completion_gui
from core.emo_systemprompt import EMO_SYSTEMPROMPT 
from core.maat_dreaming import MaatDreaming
from core.modes import (
    detect_mode,
    mode_instructions,
    build_time_context,
    build_runtime_context,
)
from core.systemprompt import MAAT_SYSTEMPROMPT as MAAT_SYSTEMPROMPT_BASE
from core.emotion_engine import EmotionEngine
from core.alignment_kernel import MaatAlignmentKernelV2
from core.memory_tools import handle_memory_commands
from core.identity_kernel import IdentityKernel
from core.thinkloop import ThinkLoop

# ----------------------------------------
# PROFILE LOADER
# ----------------------------------------
from system.profile_loader import ProfileLoader

# ----------------------------------------
# PLUGINS
# ----------------------------------------
from plugins.plugin_loader import PluginManager

# ----------------------------------------
# INIT
# ----------------------------------------
init(autoreset=True)
speed_trainer = AutoProfileSpeedTrainer()
ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(ROOT, "models")
LOG_DIR = os.path.join(ROOT, "logs")
DATA_DIR = os.path.join(ROOT, "data")
AUTOR_MODE = False
autor_used_this_turn = False
autor_escape = False


os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "memory.db")

# ----------------------------------------
# GLOBAL ENGINES / STATE
# ----------------------------------------
persona = PersonaEngine()
memory = SQLiteMemory(DB_PATH)
reflex = MaatReflexion()
emotion_engine = EmotionEngine()
alignment_kernel = MaatAlignmentKernelV2(emo_mode=EMO_MODE)
identity_kernel  = IdentityKernel(emo_mode=EMO_MODE)
quest_engine = QuestEngine()
episodic = EpisodicMemory(os.path.join(DATA_DIR, "episodic_memory.db"))

# 👇 WICHTIG: konsistenter Name sem_mem
sem_mem = SemanticMemory(os.path.join(DATA_DIR, "semantic_memory.db"))

brain = BrainMemory(episodic, sem_mem)
mie = MaatIntuitionEngine()
emm = EmotionMaatMapper()
ltm = LongTermMemory(DB_PATH)
thinkloop = ThinkLoop()
self_evo = SelfEvolutionEngine(memory, alignment_kernel, identity_kernel)

# Gehirn-Schlaf / Nachtkonsolidierung
dreaming = MaatDreaming(
    db_path_ltm=DB_PATH,
    db_path_semantic=os.path.join(DATA_DIR, "semantic_memory.db"),
)

# Optional AGI memory helpers – defensiv initialisieren
try:
    narrative = MemoryNarrative(memory)
except Exception:
    narrative = None

try:
    # 👇 hier ebenfalls: sem_mem statt semantisch/undefiniert
    fusion = MemoryFusion(memory, sem_mem)
except Exception:
    fusion = None

try:
    anchors = ContextAnchor(memory)
except Exception:
    anchors = None

try:
    backup = MemoryBackup(DB_PATH)
except Exception:
    backup = None

START_TIME = time.time()
LAST_REPLY_TIME = time.time()

# ----------------------------------------
# PROFILE SYSTEM
# ----------------------------------------
profile_loader = ProfileLoader(ROOT)

def set_emo_mode(on: bool):
    global EMO_MODE, alignment_kernel, identity_kernel
    EMO_MODE = on
    alignment_kernel.set_emo_mode(on)
    identity_kernel.set_emo_mode(on)



# ======================================================================
# MODEL CHOICE
# ======================================================================
def choose_model():
    print("──────────────────────────────────────────────")
    print("🌿 MAAT-KI — Modell auswählen")
    print("──────────────────────────────────────────────")

    models = [m for m in os.listdir(MODEL_DIR) if m.endswith(".gguf")]
    if not models:
        print(Fore.RED + "❗ Keine Modelle gefunden!")
        raise SystemExit(1)

    for i, m in enumerate(models, 1):
        print(f"[{i}] {m}")

    while True:
        try:
            c = int(input("\n🔢 Auswahl: "))
            if 1 <= c <= len(models):
                return os.path.join(MODEL_DIR, models[c - 1])
        except ValueError:
            pass
        print(Fore.RED + "Bitte eine gültige Zahl eingeben.")


# ======================================================================
# PROFILE CHOICE
# ======================================================================
def choose_profile():
    profiles = profile_loader.available_profiles()

    print("──────────────────────────────────────────────")
    print("🌿 MAAT-KI — Profil auswählen")
    print("──────────────────────────────────────────────")

    for i, p in enumerate(profiles, 1):
        print(f"[{i}] {p}")

    choice = input("\n🔢 Auswahl: ").strip()

    try:
        idx = int(choice) - 1
        return profile_loader.load_profile(profiles[idx])
    except Exception:
        print(Fore.RED + "⚠ Ungültig → Fallback auf 'harmonic'")
        return profile_loader.load_profile("harmonic")


# ======================================================================
# PERFORMANCE CHOICE
# ======================================================================
def choose_performance():
    print("\n──────────────────────────────────────────────")
    print("⚙️ Performance-Modus")
    print("──────────────────────────────────────────────")
    print("[1] HIGH (16k Kontext)")
    print("[2] MEDIUM (8k)")
    print("[3] LOW (4k)")
    print("[4] ULTRA LOW (2k)")

    profiles = {
        "1": dict(n_ctx=16000, temperature=0.7, top_p=0.9),
        "2": dict(n_ctx=8000, temperature=0.8, top_p=0.92),
        "3": dict(n_ctx=4096, temperature=0.9, top_p=0.95),
        "4": dict(n_ctx=2048, temperature=1.0, top_p=0.98),
    }

    choice = input("\n🔢 Auswahl: ").strip()
    return profiles.get(choice, profiles["1"])


# ======================================================================
# TTS CHOICE
# ======================================================================
def choose_tts():
    import platform
    osname = platform.system().lower()

    print("\n🔊 Ton einschalten? (ja/nein)")
    if input("> ").strip().lower() != "ja":
        print("🔇 Ton deaktiviert.\n")
        return None

    # macOS
    if osname == "darwin":
        print("\n🎤 macOS Stimme wählen:")
        print("[1] Alex (Standard)")
        print("[2] Victoria")
        print("[3] Daniel (UK)")
        print("[4] Samantha (US Female)")
        c = input("> ").strip()

        from tts.say_tts import SayTTS

        voices = {
            "1": "Alex",
            "2": "Victoria",
            "3": "Daniel",
            "4": "Samantha",
        }

        voice = voices.get(c, "Alex")
        return SayTTS(voice=voice)

    # Linux
    if osname == "linux":
        print("\n🎤 Stimme auswählen:")
        print("[1] eSpeak (präzise, schnell)")
        print("[2] Speech Dispatcher (spd-say)")
        c = input("> ").strip()

        if c == "2":
            from tts.spd_tts import SpdTTS
            return SpdTTS()
        else:
            from tts.espeak_tts import EspeakTTS
            return EspeakTTS(voice="de")

    # Windows (optional)
    if osname == "windows":
        print("🎤 Windows TTS wird vorbereitet…")
        try:
            from tts.win_tts import WinTTS
            return WinTTS()
        except Exception:
            print("⚠ Windows-TTS nicht installiert.")
            return None

    return None


# ======================================================================
# CHAT LOOP
# ======================================================================
def chat():
    global LAST_REPLY_TIME, AUTOR_MODE, autor_used_this_turn, autor_escape

    print(Fore.GREEN + "\n🌿 Starte MAAT-KI …\n")
    # PROFILE
    profile = choose_profile()
    profile_prompt = profile["systemprompt"]

    # TIME CONTEXT
    time_context = build_time_context()
    LAST_REPLY_TIME = time.time()
    runtime_context = build_runtime_context(LAST_REPLY_TIME)
    if EMO_MODE:
        base_prompt = EMO_SYSTEMPROMPT
    else:
        base_prompt = MAAT_SYSTEMPROMPT_BASE
        
    # SYSTEMPROMPT BUILDING
    combined_prompt = (
        MAAT_SYSTEMPROMPT_BASE
        + "\n\n"
        + f"### PROFIL: {profile['name'].upper()} ###\n"
        + profile_prompt
        + "\n\n"
        + time_context
        + "\n"
        + runtime_context
    )

    print(Fore.GREEN + f"Aktives Profil: {profile['name']}\n")

    # PLUGINS
    plugin_manager = PluginManager(ROOT)
    plugin_manager.load_plugins()

    # TTS
    tts = choose_tts()

    # STREAMING
    output_queue: "queue.Queue[str]" = queue.Queue()

    def gui_output_reader(q: "queue.Queue[str]"):
        while True:
            chunk = q.get()
            print(chunk, end="", flush=True)

    threading.Thread(
        target=gui_output_reader,
        args=(output_queue,),
        daemon=True
    ).start()

    # --------------------------------------------------
    # CONVERSATION BASIS
    # --------------------------------------------------
    conversation = [
        {"role": "system", "content": combined_prompt},
        {"role": "system", "content": memory.last_context()},
    ]

    # --------------------------------------------------
    # PERSONA-BLOCK
    # --------------------------------------------------
    style = persona.get_style_bias()
    traits = persona.get_trait_snapshot()

    conversation.append({
        "role": "system",
        "content": (
            f"[PERSONA]\n"
            f"Traits: {traits}\n"
            f"Style Bias: {style}\n"
            "Nutze diese Persona-Parameter für Ton, Tiefe und Wärme der Antwort."
        )
    })

    # LLM
    model_path = choose_model()
    perf = choose_performance()
    llm = load_llm(model_path, perf)

    print(Fore.CYAN + "📘 Nutze /hilfe für Befehle.\n")
    print(Fore.GREEN + "Du kannst jetzt der KI schreiben. Erste Antwort dauert etwas.\n")

    first_reply = True

    # ================================================================
    # MAIN LOOP
    # ================================================================
    while True:
        try:
            user_input = input(Fore.YELLOW + "> " + Style.RESET_ALL).strip()
            if not user_input:
                continue

            # ---------------------------------------------
            # GENERISCHE MEMORY-BEFEHLE (/memory ...)
            # ---------------------------------------------
            if handle_memory_commands(user_input, memory):
                continue

            # ---------------------------------------------
            # PROFILE SWITCH
            # ---------------------------------------------
            if user_input.startswith("/profile "):
                p = user_input.split(" ", 1)[1].strip()
                try:
                    profile = profile_loader.load_profile(p)
                    combined_prompt = (
                        MAAT_SYSTEMPROMPT_BASE
                        + "\n\n"
                        + f"### PROFIL: {p.upper()} ###\n"
                        + profile["systemprompt"]
                        + "\n\n"
                        + build_time_context()
                        + "\n"
                        + build_runtime_context(LAST_REPLY_TIME)
                    )
                    conversation[0]["content"] = combined_prompt
                    print(Fore.GREEN + f"🌿 Profil gewechselt: {p}")
                except Exception:
                    print(Fore.RED + "⚠ Fehler beim Profilwechsel")
                continue

            # ---------------------------------------------
            # AGI MEMORY HILFSBEFEHLE (falls Module aktiv)
            # ---------------------------------------------
            if user_input == "/remember story":
                if narrative is not None:
                    print(narrative.build_narrative(30))
                else:
                    print(Fore.RED + "⚠ Narrative-Modul nicht aktiv.")
                continue

            if user_input.startswith("/fusion "):
                terms = user_input.split(" ")[1:]
                if fusion is not None:
                    print(fusion.fusion(terms))
                else:
                    print(Fore.RED + "⚠ Fusion-Modul nicht aktiv.")
                continue

            if user_input.startswith("/anchor "):
                kw = user_input.split(" ", 1)[1].strip()
                if anchors is not None:
                    anchors.reinforce(kw)
                    print(f"🔗 Anchor verstärkt für: {kw}")
                else:
                    print(Fore.RED + "⚠ Anchor-Modul nicht aktiv.")
                continue

            if user_input == "/backup":
                if backup is not None:
                    print(backup.daily_backup())
                else:
                    print(Fore.RED + "⚠ Backup-Modul nicht aktiv.")
                continue

            # -------------------------------------------------
            # Modellwechsel
            # -------------------------------------------------
            if user_input.strip() == "/model":
                print(Fore.CYAN + "\n🔄 Modellwechsel gestartet…\n")
                try:
                    new_model_path = choose_model()
                    new_perf = choose_performance()
                    print(Fore.YELLOW + "\n📦 Lade neues Modell…\n")
                    llm = load_llm(new_model_path, new_perf)
                    print(
                        Fore.GREEN
                        + f"\n🌿 Modell erfolgreich gewechselt → {os.path.basename(new_model_path)}\n"
                    )
                    conversation.append(
                        {
                            "role": "system",
                            "content": f"[MODEL SWITCH] LLM wurde gewechselt zu: {os.path.basename(new_model_path)}",
                        }
                    )
                except Exception as e:
                    print(Fore.RED + f"❌ Fehler beim Modellwechsel: {e}\n")
                continue
  
            # -------------------------------------------------
            # /quest – MAAT Quest System
            # -------------------------------------------------
            if user_input.startswith("/quest"):

                try:
                    # 1) Quest-Engine ausführen
                    result = quest_engine.handle(user_input)

                    # Nachricht ausgeben
                    msg = result.get("message")
                    if msg:
                        print(Fore.CYAN + msg + "\n")

                    # 2) XP vergeben
                    reward = result.get("reward_xp")
                    quest_id = result.get("id")

                    if reward:
                        self_evo.state["xp"] = int(self_evo.state.get("xp", 0)) + int(reward)
                        self_evo._save_state()
                        print(Fore.GREEN + f"⭐ XP erhalten: +{reward} XP\n")

                    # 3) Persona-Update NUR wenn quest_id existiert
                    if quest_id and reward:
                        try:
                            persona.update_from_quest(quest_id, reward)
                        except Exception as e:
                            print(Fore.RED + f"[PERSONA UPDATE ERROR] {e}")

                except Exception as e:
                    print(Fore.RED + f"[QUEST ERROR] {e}")

                continue
            # -------------------------------------------------
            # Identitaet Befehl
            # -------------------------------------------------
            if user_input.lower() in ["/identität", "/werbistdu", "/identity"]:
                print(Fore.LIGHTCYAN_EX + identity_kernel.describe_self() + "\n")
                continue

            # -------------------------------------------------
            # /guide – Zeige die MAAT-KI Anleitung
            # -------------------------------------------------
            if user_input.strip() in ("/guide", "/anleitung"):
                print(Fore.CYAN + GUIDE_TEXT + Style.RESET_ALL)
                continue

            # -------------------------------------------------
            # /hilfe – Übersicht aller Befehle
            # -------------------------------------------------
            if user_input.strip() == "/hilfe":
                print(HELP_TEXT)
                continue
            # -------------------------------------------------
            # /memory – Kurzzeitgedächtnis-Befehle
            # -------------------------------------------------
            if user_input.startswith("/memory"):
                parts = user_input.split(" ", 2)

                # /memory → Hilfe
                if user_input.strip() == "/memory":
                    print(Fore.CYAN + "\n📘 Memory Befehle:")
                    print(Fore.GREEN + "  /memory show" + Fore.WHITE + "    – Zeigt alle Kurzzeit-Erinnerungen")
                    print(Fore.GREEN + "  /memory clear" + Fore.WHITE + "   – Löscht alle Kurzzeit-Erinnerungen")
                    print(Fore.GREEN + "  /memory search <wort>" + Fore.WHITE + " – Sucht im Kurzzeitgedächtnis")
                    print(Fore.GREEN + "  /memory delete <id>" + Fore.WHITE + " – Löscht einen bestimmten Eintrag\n")
                    continue

                # /memory show
                if len(parts) >= 2 and parts[1] == "show":
                    try:
                        rows = memory.get_all()
                        if not rows:
                            print(Fore.YELLOW + "\n📭 Keine gespeicherten Kurzzeit-Erinnerungen.\n")
                        else:
                            print(Fore.CYAN + "\n🧠 Kurzzeitgedächtnis:\n")
                            for r in rows:
                                print(Fore.GREEN + f"- [{r['id']}] ({r['role']}) {r['content']}")
                    except Exception as e:
                        print(Fore.RED + f"[MEMORY SHOW ERROR] {e}")
                    continue

                # /memory clear
                if len(parts) >= 2 and parts[1] == "clear":
                    try:
                        memory.clear()
                        print(Fore.GREEN + "\n🧹 Kurzzeitgedächtnis gelöscht!\n")
                    except Exception as e:
                        print(Fore.RED + f"[MEMORY CLEAR ERROR] {e}")
                    continue

                # /memory search <query>
                if len(parts) >= 3 and parts[1] == "search":
                    query = parts[2].strip().lower()
                    try:
                        rows = memory.search(query)
                        if not rows:
                            print(Fore.YELLOW + f"\n🔍 Keine Treffer zu '{query}'.\n")
                        else:
                            print(Fore.CYAN + f"\n🔍 Treffer zu '{query}':\n")
                            for r in rows:
                                print(Fore.GREEN + f"- [{r['id']}] ({r['role']}) {r['content']}")
                    except Exception as e:
                        print(Fore.RED + f"[MEMORY SEARCH ERROR] {e}")
                    continue

                # /memory delete <id>
                if len(parts) >= 3 and parts[1] == "delete":
                    mid = parts[2].strip()
                    try:
                        memory.delete(mid)
                        print(Fore.GREEN + f"\n🗑️ Eintrag {mid} gelöscht!\n")
                    except Exception as e:
                        print(Fore.RED + f"[MEMORY DELETE ERROR] {e}")
                    continue
            # -------------------------------------------------
            # AUTOR-MODUS
            # -------------------------------------------------
            if user_input.lower() == "autor on":
                AUTOR_MODE = True
                autor_escape = False
                print(Fore.GREEN + "🟢 Autor-Modus aktiviert (sicher).")
                print(
                    Fore.YELLOW
                    + "Tipp: Schreibe 'stop' oder 'abbruch', um Autor-Modus pro Antwort zu stoppen.\n"
                )
                continue

            if user_input.lower() in ["autor off", "autor aus"]:
                AUTOR_MODE = False
                autor_escape = False
                print(Fore.YELLOW + "⛔ Autor-Modus deaktiviert.\n")
                continue

            if user_input.lower() in ["stop", "abbruch", "halt"]:
                autor_escape = True
                print(Fore.YELLOW + "⛔ Autor-Fortsetzung für diese Antwort gestoppt.\n")
                continue

            # -------------------------------------------------
            # /dream – Nachtkonsolidierung (Maat-Dreaming)
            # -------------------------------------------------
            if user_input.strip() in ("/dream", "/sleep"):
                try:
                    report = dreaming.run_night_cycle(
                        hours_back=24,
                        max_episodes=300,
                        decay_factor=0.997,
                        delete_threshold=0.02,
                    )
                    print(Fore.MAGENTA + "\n" + report + "\n")
                except Exception as e:
                    print(Fore.RED + f"[MAAT-DREAM ERROR] {e}\n")
                continue

             # ==========================================================
            # SEMANTIC MEMORY COMMANDS (FAISS-free)
            # ==========================================================
            if user_input.startswith("/sem"):
                parts = user_input.split(" ", 2)

                # /sem → Hilfe
                if user_input.strip() == "/sem":
                    print(Fore.CYAN + "\n📘 Semantic Memory Befehle:")
                    print(Fore.CYAN + "  /sem add <text>     – Text als semantische Erinnerung speichern")
                    print(Fore.CYAN + "  /sem search <query> – semantisch ähnliche Erinnerungen finden")
                    print(Fore.CYAN + "  /sem latest         – Zeigt die letzten 10 semantischen Erinnerungen")
                    print()
                    continue

                # /sem add TEXT
                if len(parts) >= 3 and parts[1] == "add":
                    text = parts[2].strip()
                    try:
                        sem_mem.add(text)
                        print(Fore.GREEN + f"\n✅ Semantische Erinnerung gespeichert!\n   → {text}\n")
                    except Exception as e:
                        print(Fore.RED + f"[SEM ADD ERROR] {e}")
                    continue

                # /sem search QUERY
                if len(parts) >= 3 and parts[1] == "search":
                    query = parts[2].strip()
                    try:
                        results = sem_mem.search(query, limit=10)
                        if not results:
                            print(Fore.YELLOW + f"\n🔍 Keine ähnlichen Erinnerungen zu: '{query}'\n")
                        else:
                            print(Fore.CYAN + f"\n🔍 Ähnliche Erinnerungen zu '{query}':\n")
                            for r in results:
                                print(Fore.CYAN + f"- [{r['ts']}]  score={r['score']:.2f}")
                                print(Fore.WHITE + f"  {r['text']}\n")
                    except Exception as e:
                        print(Fore.RED + f"[SEM SEARCH ERROR] {e}")
                    continue

                # /sem latest → letzte 10 Einträge
                if len(parts) >= 2 and parts[1] == "latest":
                    try:
                        sem_mem.cur.execute(
                            "SELECT ts, text FROM semantic_memory ORDER BY id DESC LIMIT 10"
                        )
                        rows = sem_mem.cur.fetchall()
                        if not rows:
                            print(Fore.YELLOW + "\n📭 Noch keine semantischen Erinnerungen gespeichert.\n")
                        else:
                            print(Fore.CYAN + "\n🧠 Letzte 10 semantische Erinnerungen:\n")
                            for ts, text in rows:
                                print(Fore.CYAN + f"- [{ts}] {text}")
                    except Exception as e:
                        print(Fore.RED + f"[SEM LATEST ERROR] {e}")
                    continue
            # -------------------------------------------------
            # /game – MAAT-RPG Erklärung
            # -------------------------------------------------
            if user_input.strip() == "/game":
                print(show_game_info())
                continue
            # -------------------------------------------------
            # /perfinfo – Speed-Trainer Infos
            # -------------------------------------------------
            if user_input.strip() == "/perfinfo":
                print(Fore.CYAN + speed_trainer.pretty_info() + "\n")
                continue

            # -------------------------------------------------
            # /evo – Self-Evolution Commands
            # -------------------------------------------------
            if user_input.startswith("/evo"):
                parts = user_input.split()
                sub = parts[1].lower() if len(parts) > 1 else "status"

                if sub in ("status", "info"):
                    try:
                        status = self_evo.get_status_text()
                        print(Fore.MAGENTA + status + "\n")
                    except Exception as e:
                        print(Fore.RED + f"[EVO STATUS ERROR] {e}")

                elif sub == "log":
                    try:
                        log_txt = self_evo.get_log_text(limit=20)
                        print(Fore.MAGENTA + log_txt + "\n")
                    except Exception as e:
                        print(Fore.RED + f"[EVO LOG ERROR] {e}")

                elif sub == "rules":
                    try:
                        rules_txt = self_evo.get_rules_text()
                        print(Fore.MAGENTA + rules_txt + "\n")
                    except Exception as e:
                        print(Fore.RED + f"[EVO RULES ERROR] {e}")

                elif sub == "patches":
                    try:
                        patches_txt = self_evo.list_patches_text()
                        print(Fore.MAGENTA + patches_txt + "\n")
                    except Exception as e:
                        print(Fore.RED + f"[EVO PATCHES ERROR] {e}")

                else:
                    print(
                        Fore.MAGENTA
                        + "Verfügbare /evo-Befehle:\n"
                        "  /evo            — Status (Level, Punkte)\n"
                        "  /evo log        — Evolutions-Log\n"
                        "  /evo rules      — Regelmatrix\n"
                        "  /evo patches    — gespeicherte Patches\n"
                    )
                continue

            # ---------------------------------------------
            # /zeit – Zeitgefühl anzeigen (früh raus)
            # ---------------------------------------------
            if user_input.strip() == "/zeit":
                print(Fore.BLUE + build_runtime_context(LAST_REPLY_TIME) + "\n")
                continue

            # ---------------------------------------------
            # 1. USER MESSAGE IN GEHIRN-SPEICHER (episodic + semantic)
            #    → Slash-Befehle NICHT abspeichern
            # ---------------------------------------------
            if not user_input.startswith("/"):
                try:
                    brain.store("user", user_input)
                except Exception as e:
                    print(Fore.RED + f"[BRAIN STORE USER ERROR] {e}")

            conversation.append({"role": "user", "content": user_input})
            identity_kernel.inject_identity(conversation, user_input)

            # ---------------------------------------------
            # LANGZEIT-ERINNERUNGEN (Gehirn-Auto-Recall)
            # → kombiniert episodisch + semantisch
            # ---------------------------------------------
            mem_hits = []
            try:
                mem_hits = brain.recall(user_input, limit=5)
            except Exception as e:
                print(Fore.RED + f"[BRAIN RECALL ERROR] {e}")

            if mem_hits:
                print(Fore.BLUE + "\n📜 Langzeit-Erinnerungen (inkl. Semantik):")
                mem_lines = []
                seen = set()

                for r in mem_hits:
                    full_text = (r.get("text") or "").replace("\n", " ")
                    if not full_text or full_text in seen:
                        continue
                    seen.add(full_text)

                    ts = str(r.get("ts") or "?")
                    role = r.get("role", "memory")
                    cat = r.get("category", "allgemein")

                    snippet = full_text if len(full_text) <= 160 else full_text[:157] + "..."

                    # Terminal-Ausgabe
                    print(Fore.BLUE + f"  - [{ts}] ({role}) <{cat}> {snippet}")

                    # Volltext für Prompt-Block
                    mem_lines.append(f"[{ts}] ({role}) <{cat}> {full_text}")

                print(Style.RESET_ALL)

                mem_block = (
                    "Die folgenden Einträge stammen aus deinem Gehirn-Speicher "
                    "(episodisch + semantisch). Nutze sie als Erinnerungs-Kontext.\n"
                    "[LONG_TERM_MEMORY]\n"
                    + "\n".join(mem_lines)
                )

                conversation.append({"role": "system", "content": mem_block})
            # ---------------------------------------------
            # MODE
            # ---------------------------------------------
            mode = detect_mode(user_input)
            conversation.append(
                {
                    "role": "system",
                    "content": f"[MODE: {mode}] {mode_instructions(mode)}",
                }
            )

            print(Fore.YELLOW + "\n🤖 KI denkt…" + Style.RESET_ALL)
            print(Fore.GREEN + "→ ", end="", flush=True)

            speak_fn = tts.speak_chunk if tts else None

            # -------------------------------------------------
            # THINKING MODE – falls der User es verlangt
            # -------------------------------------------------
            if thinkloop.needs_think(user_input):
                print(Fore.MAGENTA + "🧠 Denkmodus aktiviert…" + Style.RESET_ALL)
                internal_thoughts = thinkloop.run_thinkloop(llm, conversation)
                conversation.append(
                    {"role": "system", "content": f"[THOUGHTS]\n{internal_thoughts}"}
                )

            # -------------------------------------------------
            # LLM ANTWORT
            # -------------------------------------------------
            reply_text = stream_completion_gui(
                llm,
                conversation,
                gui_queue=output_queue,
                speak_fn=speak_fn,
                show_progress=first_reply,
            )

            # -------------------------------------------------
            # AUTOR-MODUS (sicher, einmal pro Runde)
            # -------------------------------------------------
            if AUTOR_MODE and not autor_used_this_turn and not autor_escape:
                autor_used_this_turn = True

                continuation_prompt = (
                    "Fahre die vorherige Antwort in maximal 3 klaren Sätzen fort. "
                    "Keine Wiederholung. Kein erneutes Denken. Keine Schleife. "
                    "Nur eine natürliche Ergänzung."
                )

                conversation.append({
                    "role": "system",
                    "content": "[AUTOR] " + continuation_prompt
                })

                # zweite, kurze Fortsetzungs-Generation
                continuation = stream_completion_gui(
                    llm,
                    conversation,
                    gui_queue=output_queue,
                    speak_fn=speak_fn,
                    show_progress=False,
                )

                print(Fore.CYAN + "\n✍️ Autor-Fortsetzung:\n" + continuation + "\n")

                # Abschluss merken
                conversation.append({"role": "assistant", "content": continuation})
            else:
                autor_used_this_turn = False
                autor_escape = False

            # Identity-Korrektur
            reply_text = identity_kernel.sanitize(reply_text)

            # Alignment-Anpassung
            aligned_text, align_meta = alignment_kernel.align(reply_text)
            reply_text = aligned_text

            maat_score = align_meta.get("maat_score", 0.0)
            print(Fore.GREEN + f"🌿 Maat-Score: {maat_score:.2f}")
            first_reply = False
            print("\n")

            # ---------------------------------------------
            # ALIGNMENT EVAL
            # ---------------------------------------------
            try:
                aligned_reply = alignment_kernel.evaluate(reply_text)
            except Exception:
                aligned_reply = reply_text

            # ---------------------------------------------
            # REFLEXION
            # ---------------------------------------------
            thought = reflex.generate_reflexion_question(user_input, aligned_reply)
            print(Fore.CYAN + f"\n💭 Gedanke: {thought}\n")

            # ---------------------------------------------
            # RUNTIME FEELING
            # ---------------------------------------------
            print(Fore.BLUE + build_runtime_context(LAST_REPLY_TIME) + "\n")
            LAST_REPLY_TIME = time.time()


            # ---------------------------------------------
            # EMOTION + EMM
            # ---------------------------------------------
            try:
                # Emotion Engine
                e_raw = emotion_engine.detect_raw(user_input)
                E_KI = emotion_engine.compute_emotion(
                    e_raw, H=0.8, V=0.85, deltaD=0.1, R=1.0
                )
                emo_txt = emotion_engine.transform(e_raw)
                safe_info = emotion_engine.safe(e_raw, E_KI)

                # EMM: Emotion → Maat-Vektor
                mie_weights = emm.map(emo_txt, intensity=abs(E_KI))

                print(Fore.LIGHTCYAN_EX + f"🌀 EMM-Maat-Vektor: {mie_weights}\n")
                print(Fore.LIGHTBLUE_EX + f"💙 Emotion: {emo_txt} ({E_KI:.2f})")
                print(Fore.LIGHTBLUE_EX + f"💬 Sicherheit: {safe_info}\n")

            except Exception as e:
                print(Fore.RED + f"[EMOTION/EMM ERROR] {e}")

            # ---------------------------------------------
            # Emotion → Persona-Anpassung
            # ---------------------------------------------
            try:
                e_raw = emotion_engine.detect_raw(user_input)
                E_KI = emotion_engine.compute_emotion(
                    e_raw, H=0.8, V=0.85, deltaD=0.1, R=1.0
                )
                emo_txt = emotion_engine.transform(e_raw)

                # Persona lernt aus Emotion
                persona.update_from_emotion(e_raw, abs(E_KI))

            except Exception as e:
                print(Fore.RED + f"[PERSONA EMOTION ERROR] {e}")

            # ---------------------------------------------
            # B_KI + Emotion
            # ---------------------------------------------
            try:
                base_bki = reflex.compute_b_ki(aligned_reply, user_input, conversation)
                mod_bki = base_bki * (1 + 0.25 * E_KI)
                print(Fore.MAGENTA + f"🜂 B_KI: {mod_bki:.2f}\n")
            except Exception as e:
                print(Fore.RED + f"[B_KI ERROR] {e}")

            # ---------------------------------------------
            # Identity-Drift
            # ---------------------------------------------
            try:
                id_drift = identity_kernel.measure_drift(aligned_reply)
                print(Fore.YELLOW + f"🔶 Identity-Drift: {id_drift:.2f}\n")
            except Exception as e:
                id_drift = 0.0
                print(Fore.RED + f"[IDENTITY DRIFT ERROR] {e}")

            # ---------------------------------------------
            # Maat-Intuition Engine
            # ---------------------------------------------
            try:
                mie_info = mie.evaluate(
                    user_input,
                    maat_vec={"H":0.8,"B":0.85,"S":0.9,"V":0.88,"R":0.92},
                    emotion=E_KI,
                    drift=id_drift
                )

                print(Fore.MAGENTA + f"🔮 Intuition: {mie_info['intuition']:.2f}")
                print(Fore.MAGENTA + f"✨ Intent: {mie_info['intent']}")
                print(Fore.MAGENTA + f"🌿 Resonanz: {mie_info['resonance']:.2f}\n")

                # Die Intuition beeinflusst die Antwort
                conversation.append({
                    "role": "system",
                    "content": f"[MIE] intuition={mie_info['intuition']:.2f} intent={mie_info['intent']}"
                })

            except Exception as e:
                print(Fore.RED + f"[MIE ERROR] {e}")

            # ---------------------------------------------
            # Self-Evolution Engine
            # ---------------------------------------------
            try:
                meta_data = {
                    "maat_score": maat_score,
                    "emotion": E_KI,
                    "identity_drift": id_drift,
                }

                patch = self_evo.evaluate_and_evolve(aligned_reply, meta_data)

                if patch:
                    if patch.get("status") == "blocked":
                        print(
                            Fore.YELLOW
                            + f"⚠️ Selbst-Evolution blockiert (Limit erreicht): {patch['reason']}\n"
                        )
                    else:
                        self_evo.print_patch(patch)
            except Exception as e:
                print(Fore.RED + f"[SELF-EVO ERROR] {e}")

            # ---------------------------------------------
            # 5. ASSISTANT-ANTWORT SPEICHERN (Gehirn + Kurzzeitgedächtnis)
            # ---------------------------------------------
            try:
                memory.add("assistant", reply_text)
            except Exception as e:
                print(Fore.RED + f"[SPEICHERN ERROR] {e}")

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\n🌿 MAAT-KI beendet sich sanft. Auf Wiedersehen!\n")
            break

        except Exception as e:
            print(Fore.RED + f"\nUnerwarteter Fehler im Chat-Loop: {e}")
            continue
# ======================================================================
# START DES PROGRAMMS
# ======================================================================
if __name__ == "__main__":
    chat()