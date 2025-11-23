def run_chat_loop(
    llm,
    tts,
    persona,
    self_evo,
    quest_engine,
    identity_kernel,
    alignment_kernel,
    emotion_engine,
    reflex,
    thinkloop,
    memory,
    brain,
    mie,
    emm,
    GUIDE_TEXT,
    HELP_TEXT,
    MAAT_SYSTEMPROMPT_BASE,
    choose_profile,
    choose_model,
    choose_performance,
    choose_tts,
    build_time_context,
    build_runtime_context,
    PluginManager,
    speed_trainer,
    dreaming,
    narrative,
    fusion,
    anchors,
    backup
):
    import time
    import queue
    import threading
    from colorama import Fore, Style

    global LAST_REPLY_TIME, AUTOR_MODE, autor_used_this_turn, autor_escape

    # ---------------------------------------------
    # INITIALISIERUNG
    # ---------------------------------------------
    print(Fore.GREEN + "\n🌿 Starte MAAT-KI …\n")

    profile = choose_profile()
    profile_prompt = profile["systemprompt"]

    time_context = build_time_context()
    LAST_REPLY_TIME = time.time()
    runtime_context = build_runtime_context(LAST_REPLY_TIME)

    combined_prompt = (
        MAAT_SYSTEMPROMPT_BASE
        + f"\n\n### PROFIL: {profile['name'].upper()} ###\n"
        + profile_prompt
        + "\n\n"
        + time_context
        + "\n"
        + runtime_context
    )

    print(Fore.GREEN + f"Aktives Profil: {profile['name']}\n")

    # Plugins
    plugin_manager = PluginManager(os.path.dirname(os.path.abspath(__file__)))
    plugin_manager.load_plugins()

    # TTS
    tts = choose_tts()

    # GUI-Streaming Queue
    output_queue = queue.Queue()

    def reader(q):
        while True:
            chunk = q.get()
            print(chunk, end="", flush=True)

    threading.Thread(target=reader, args=(output_queue,), daemon=True).start()

    # Persona Snapshot
    persona_meta = {
        "role": "system",
        "content": (
            f"[PERSONA]\nTraits: {persona.get_trait_snapshot()}\n"
            f"Style Bias: {persona.get_style_bias()}\n"
            "Nutze diese Parameter für Ton, Tiefe und Wärme."
        ),
    }

    # Gespräch starten
    conversation = [
        {"role": "system", "content": combined_prompt},
        persona_meta,
        {"role": "system", "content": memory.last_context()},
    ]

    # Modellwahl
    model_path = choose_model()
    perf = choose_performance()
    llm = load_llm(model_path, perf)

    print(Fore.CYAN + "📘 Nutze /hilfe für Befehle.\n")
    print(Fore.GREEN + "Du kannst jetzt der KI schreiben. Erste Antwort dauert etwas.\n")

    first_reply = True

    # ---------------------------------------------
    # HAUPTSCHLEIFE
    # ---------------------------------------------
    while True:
        try:
            user_input = input(Fore.YELLOW + "> " + Style.RESET_ALL).strip()
            if not user_input:
                continue

            # Memory commands
            from core.memory_tools import handle_memory_commands
            if handle_memory_commands(user_input, memory):
                continue

            # Profile switch
            if user_input.startswith("/profile "):
                try:
                    new = user_input.split(" ", 1)[1]
                    profile = profile_loader.load_profile(new)
                    combined_prompt = (
                        MAAT_SYSTEMPROMPT_BASE
                        + f"\n\n### PROFIL: {new.upper()} ###\n"
                        + profile["systemprompt"]
                        + "\n\n"
                        + build_time_context()
                        + "\n"
                        + build_runtime_context(LAST_REPLY_TIME)
                    )
                    conversation[0]["content"] = combined_prompt
                    print(Fore.GREEN + f"🌿 Profil gewechselt → {new}")
                except:
                    print(Fore.RED + "⚠ Fehler beim Profilwechsel")
                continue

            # -----------------------------
            # QUEST SYSTEM
            # -----------------------------
            if user_input.startswith("/quest"):
                try:
                    result = quest_engine.handle(user_input)
                    msg = result.get("message", "")
                    if msg:
                        print(Fore.CYAN + msg + "\n")

                    reward = result.get("reward_xp")
                    if reward:
                        self_evo.state["xp"] = int(self_evo.state.get("xp", 0)) + int(reward)
                        self_evo._save_state()
                        print(Fore.GREEN + f"⭐ +{reward} XP\n")

                    try:
                        persona.update_from_quest(result.get("id"), reward)
                    except Exception as e:
                        print(Fore.RED + f"[PERSONA UPDATE ERROR] {e}")

                except Exception as e:
                    print(Fore.RED + f"[QUEST ERROR] {e}")

                continue

            # -----------------------------
            # SHOW HELP
            # -----------------------------
            if user_input == "/hilfe":
                print(HELP_TEXT)
                continue

            if user_input in ("/guide", "/anleitung"):
                print(GUIDE_TEXT)
                continue

            # -----------------------------
            # DREAMING
            # -----------------------------
            if user_input in ["/dream", "/sleep"]:
                try:
                    report = dreaming.run_night_cycle(
                        hours_back=24, max_episodes=250, decay_factor=0.997
                    )
                    print(Fore.MAGENTA + report + "\n")
                except Exception as e:
                    print(Fore.RED + f"[DREAM ERROR] {e}")
                continue

            # -----------------------------
            # BRAIN STORE USER
            # -----------------------------
            if not user_input.startswith("/"):
                try:
                    brain.store("user", user_input)
                except Exception as e:
                    print(Fore.RED + f"[BRAIN STORE ERROR] {e}")

            conversation.append({"role": "user", "content": user_input})

            # Identity Kernel
            identity_kernel.inject_identity(conversation, user_input)

            # -----------------------------
            # AUTO RECALL (episodic+semantic)
            # -----------------------------
            try:
                hits = brain.recall(user_input, limit=5)
            except:
                hits = []

            if hits:
                block = ["[LONG_TERM_MEMORY]"]
                print(Fore.BLUE + "\n📜 Erinnerungen:")

                for r in hits:
                    txt = (r.get("text") or "").replace("\n", " ")
                    if not txt:
                        continue
                    print(Fore.BLUE + f"  - {txt[:120]}…")
                    block.append(txt)

                conversation.append(
                    {"role": "system", "content": "\n".join(block)}
                )

            # -----------------------------
            # MODE
            # -----------------------------
            from core.modes import detect_mode, mode_instructions
            mode = detect_mode(user_input)
            conversation.append({
                "role": "system",
                "content": f"[MODE: {mode}] {mode_instructions(mode)}",
            })

            print(Fore.YELLOW + "\n🤖 KI denkt…" + Style.RESET_ALL)
            print(Fore.GREEN + "→ ", end="", flush=True)

            speak_fn = tts.speak_chunk if tts else None

            # THINKLOOP
            if thinkloop.needs_think(user_input):
                internal = thinkloop.run_thinkloop(llm, conversation)
                conversation.append({"role": "system", "content": f"[THOUGHTS]\n{internal}"})

            # -----------------------------
            # LLM ANTWORT
            # -----------------------------
            reply = stream_completion_gui(
                llm,
                conversation,
                gui_queue=output_queue,
                speak_fn=speak_fn,
                show_progress=first_reply,
            )

            first_reply = False

            # Sanitizing
            reply = identity_kernel.sanitize(reply)

            # Alignment
            aligned, meta = alignment_kernel.align(reply)
            reply = aligned

            print(Fore.GREEN + f"🌿 Maat-Score: {meta.get('maat_score',0):.2f}\n")

            # Reflexion
            thought = reflex.generate_reflexion_question(user_input, reply)
            print(Fore.CYAN + f"💭 Gedanke: {thought}\n")

            LAST_REPLY_TIME = time.time()

            # -----------------------------
            # EMOTION + EMM + MIE
            # -----------------------------
            try:
                raw = emotion_engine.detect_raw(user_input)
                E = emotion_engine.compute_emotion(raw, H=0.8, V=0.85, deltaD=0.1)
                emo_txt = emotion_engine.transform(raw)

                mie_vec = emm.map(emo_txt, intensity=abs(E))

                print(Fore.LIGHTCYAN_EX + f"🌀 EMM: {mie_vec}")
                persona.update_from_emotion(raw, abs(E))
            except Exception:
                pass

            # B_KI
            try:
                bki_base = reflex.compute_b_ki(reply, user_input, conversation)
                bki_mod = bki_base * (1 + 0.2 * E)
                print(Fore.MAGENTA + f"🜂 B_KI: {bki_mod:.2f}")
            except:
                pass

            # Intuition Engine
            try:
                mie_info = mie.evaluate(
                    user_input,
                    maat_vec={"H": 0.8, "B": 0.85, "S": 0.9, "V": 0.88, "R": 0.92},
                    emotion=E,
                )
                print(Fore.MAGENTA + f"🔮 Intuition: {mie_info['intuition']:.2f}")
                conversation.append({
                    "role": "system",
                    "content": f"[MIE] intuition={mie_info['intuition']:.2f}"
                })
            except:
                pass

            # Self-Evolution
            try:
                patch = self_evo.evaluate_and_evolve(
                    reply,
                    {
                        "emotion": E,
                        "maat_score": meta.get("maat_score", 0),
                    },
                )
                if patch:
                    self_evo.print_patch(patch)
            except:
                pass

            # Save assistant message
            try:
                memory.add("assistant", reply)
            except:
                pass

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n🌿 MAAT-KI beendet sich sanft.\n")
            break

        except Exception as e:
            print(Fore.RED + f"❌ Unerwarteter Fehler: {e}")
            continue