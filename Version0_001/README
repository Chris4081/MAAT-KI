# MAAT-KI v0.001 (Preview, Deutsch)

MAAT-KI ist ein **lokaler KI-Agent**, der ein GGUF-LLM mit einem ethischen, gedächtnisbasierten Rahmen kombiniert.  
Im Zentrum stehen die fünf Maat‑Prinzipien: **Harmonie, Balance, Schöpfungskraft, Verbundenheit, Respekt**.

> Status: **Experimenteller Prototyp** – nur für lokale Tests gedacht.

---

## Hauptfunktionen

- 🔹 **Lokales LLM (llama.cpp / GGUF)**  
  - Getestet u. a. mit  
    - `Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf`  
    - `openchat-3.6-8b-20240522-imat-Q4_0.gguf`  
  - Performance‑Profile (2k–16k Kontext), **HIGH (16k)** empfohlen.

- 🔹 **Maat-Systemprompt & Alignment**  
  - Antworten werden nach den fünf Prinzipien bewertet.  
  - Selbstreflexion & PLP‑Formel zur Reduktion von Halluzinationen.  
  - Maat‑Logs: Score, Emotion, Intuition, Resonanz.

- 🔹 **Gedächtnis-System**  
  - Kurzzeit‑Memory (Chatverlauf, `/memory …`).  
  - Episodisches Gedächtnis (ganze Sätze).  
  - Semantisches Gedächtnis (Fakten & Vorlieben, `/sem …`).  
  - Maat‑Dreaming: Nacht‑Konsolidierung per `/dream`.

- 🔹 **Self‑Evolution Engine**  
  - Beobachtet Maat‑Score, Emotion, Identity‑Drift.  
  - Zeigt Entwicklungsstand & Patches über `/evo`, `/evo log`.

- 🔹 **GUI (PySide6)**  
  - ChatGPT‑ähnliche Oberfläche (`maat_gui.py`).  
  - Chat‑Bubbles, Dark/Light‑Mode, Auto‑Scroll.  
  - Kleine Status‑Bubbles für Maat‑Score, Emotion, Intuition etc.  
  - Startet `MAAT-KI.py` als Subprozess (PTY), keine Änderungen nötig.

---

## Voraussetzungen

- Python **3.10+**
- Empfohlen: macOS oder Linux (für PTY + TTS)
- GGUF‑Modell im Ordner `models/`, z. B.:  
  - `Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf`  
  - oder `openchat-3.6-8b-20240522-imat-Q4_0.gguf`

### Python-Abhängigkeiten (Kern)

In `requirements.txt` u. a.:

```txt
colorama
llama-cpp-python
pyttsx3
numpy
scipy
regex
tqdm
sentencepiece
sqlitedict
python-dateutil
pydantic
```

### Zusätzliche Abhängigkeit für die GUI

```txt
PySide6
```

Installation z. B. mit:

```bash
python3 -m venv maattestgit-env
source maattestgit-env/bin/activate   # Windows: maattestgit-env\Scripts\activate
pip install -r requirements-macarm.txt
pip install PySide6
```

---

## Projektstruktur (Kurzform)

```txt
MAAT-KI/
├─ MAAT-KI.py          # Kern-Chatloop und Kernprogramm (Terminal)
├─ maat_gui.py         # PySide6 GUI (ChatGPT-Style)
├─ core/               # Engines (Memory, Emotion, Evolution, Persona, etc.)
├─ system/             # Profile, Hilfe, Guide
├─ plugins/            # Erweiterungen (TTS, Websearch, Memory-Tools …)
├─ models/             # GGUF-Modelle
├─ data/               # SQLite-Memory & Logs
└─ logs/               # Laufzeit-Logs
```

---

## Nutzung

### 1. Modell ablegen

Lege ein kompatibles GGUF‑Modell in `models/`, z. B.:

```txt
models/Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf
```

### 2. Terminal-Version starten

```bash
python3 MAAT-KI.py
```

Im Startdialog:

1. Profil wählen (z. B. `harmonic`).  
2. TTS auswählen (optional).  
3. Modell auswählen.  
4. Performance‑Modus wählen (**HIGH** empfohlen, solange VRAM/ RAM reicht).

### 3. GUI-Version starten

```bash
python3 maat_gui.py
```

- Öffnet ein Fenster mit ChatGPT‑ähnlicher Oberfläche.  
- Verbindet sich per PTY mit `MAAT-KI.py`.  
- Terminal‑Fragen (Profil, Modell, TTS) beantwortest du im Chatfenster.

---

## Wichtige Befehle (Auswahl)

- `/hilfe` oder `/guide` – Hilfe & Überblick.  
- `/profile harmonic` – Profil wechseln.  
- `/model` – Modell im laufenden Betrieb wechseln.  
- `/memory show/search/clear` – episodische Erinnerungen.  
- `/sem add/search/latest` – semantische Erinnerungen.  
- `/dream` – Maat‑Dreaming (Schlaf‑Konsolidierung).  
- `/evo`, `/evo log` – Self‑Evolution‑Status & Verlauf.  
- `/emotion` – Emotionale Analyse.  
- `/reflex` – Reflexionsfrage.  

Du kannst außerdem jederzeit Maat‑Bewertungen anfordern, z. B.:

- „Berechne den Maat‑Wert des Eiffelturms.“  
- „Bewerte diese Firma nach Maat.“  
- „Schätze die Stabilität dieser Idee mit der PLP‑Formel.“

---

## Lizenz

Dieses Projekt steht unter der **GNU Affero General Public License v3.0 (AGPL‑3.0)**.  
Siehe die Datei `LICENSE` für Details.

---

## Hinweis

MAAT-KI v0.001 ist ein **Forschungs‑ und Experimentalsystem**.  
Keine Garantie auf Korrektheit, Sicherheit oder Stabilität.  
Bitte nur lokal und eigenverantwortlich einsetzen.
