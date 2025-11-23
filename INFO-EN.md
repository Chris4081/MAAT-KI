# MAAT-KI – Project Info (EN)

**Version:** 0.001 (Early Experimental Prototype)  
**Status:** Local research project – not production ready

---

## What is MAAT-KI?

MAAT-KI is a **local AI agent** that combines classic LLM capabilities with an **ethical, memory-driven framework** based on the Egyptian principle of *Maat*.

Core values (Maat principles):

- 🌿 **Harmony (H)** – clarity, coherence, internal consistency  
- ⚖️ **Balance (B)** – depth vs. simplicity, logic vs. creativity  
- 🎨 **Creativity (S)** – new ideas, synthesis, generative thinking  
- 🌐 **Connectedness (V)** – context, relationships, systems thinking  
- 🕊️ **Respect (R)** – dignity, safety, ethical awareness  

The goal: explore how a local LLM can **evolve**, remember and reflect in a way that stays aligned with these five principles.

---

## Main Components

### 1. Local LLM Backend

- Runs completely **offline** using `llama-cpp-python` and **GGUF** models.
- Tested with e.g.  
  - `Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf`  
  - `openchat-3.6-8b-20240522-imat-Q4_0.gguf`
- Recommended: **HIGH** performance mode (16k context) if your hardware allows it.

### 2. Maat System Prompt & Alignment

- Central system prompt encodes the Maat principles.
- A custom **Alignment Kernel** evaluates each answer:
  - Estimates Harmony, Balance, Creativity, Connectedness, Respect.
  - Can down‑tune or rephrase unsafe / low‑Maat responses.
- A **PLP formula** (Problem‑Solving Potential) scores how useful a response is.

### 3. Memory Stack

MAAT-KI experiments with a multi‑layer memory system:

- **Short‑term memory (SQLite)** – current conversation context.  
- **Episodic memory** – full chat episodes, similar to human memories.  
- **Semantic memory** – facts & stable knowledge (e.g. user preferences).  
- **BrainMemory & LongTermMemory** – merge, prioritise and decay memories.  
- **Dreaming mode** – a “night cycle” that consolidates memories.

You can interact with this via simple commands like `/memory`, `/sem`, `/dream` (in the German version).

### 4. Emotion, Identity & Self‑Evolution

- **Emotion Engine** – tries to detect basic emotional tone (e.g. neutral, sad) and adjust the answer style.
- **Identity Kernel** – keeps the agent’s “self‑image” stable.
- **Self‑Evolution Engine** – logs interactions and proposes small internal tweaks (rules, weights, preferences).

This is **research**, not a medical or psychological tool.

### 5. GUI (PySide6 Desktop Chat)

- Optional **desktop chat UI** (`maat_gui.py`) built with **PySide6**.
- Features:
  - ChatGPT‑like bubbles
  - Dark/Light mode toggle
  - Auto‑scroll during streaming
  - Separate status bubbles for Maat‑Score, Emotion, Intuition, etc.
- The GUI starts `MAAT-KI.py` as a **subprocess** via PTY – the core engine remains unchanged.

---

## Goals & Non‑Goals

**Goals**

- Explore **ethical, memory‑rich local AI**.
- Experiment with formulas like **Maat Value**, **PLP**, **Consciousness / Resonance indices**.
- Provide a transparent playground for:
  - Researchers
  - Tinkerers
  - Artists & system thinkers

**Non‑Goals**

- Not a drop‑in replacement for ChatGPT or commercial assistants.
- Not optimised for speed, scalability or UX perfection.
- Not a clinical or safety‑critical system.

---

## License

The project is released under the **GNU Affero General Public License v3 (AGPL‑3.0)**.

This means:

- You are free to **use, study, modify and share** the code.
- If you run a **modified version as a network service**, you must provide the source code of your modifications to users.

Please read the bundled `LICENSE` file for the full legal text.

---

## Disclaimer

MAAT-KI is an **early experimental prototype**.  
Outputs may be **incorrect, biased or incomplete**.

Use it responsibly, double‑check important results, and do not rely on it for critical decisions.
