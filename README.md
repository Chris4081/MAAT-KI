# MAAT-KI – Lokaler ethischer KI-Agent

MAAT-KI ist ein lokaler KI-Agent, der klassische LLM‑Funktionalität mit einem ethischen, gedächtnisbasierten Framework verbindet.  
Im Zentrum stehen die fünf Maat‑Prinzipien:

- 🌿 **Harmonie**
- ⚖️ **Balance**
- 🎨 **Schöpfungskraft**
- 🌐 **Verbundenheit**
- 🕊️ **Respekt**

Gebaut auf Python, komplett offline nutzbar – selbst auf älterer Hardware.

---

## 🚀 Kernfunktionen

### **1. Core Engine**
- Lokales LLM‑Backend (GGUF, llama.cpp)
- Anpassbare Profile: Temperatur, Top‑p, Kontextgröße
- Dynamische Persona‑Engine (Ton, Tiefe, Stil)
- Maat-Systemprompt für ethische, klare Antworten
- PLP‑Formel zur Qualitätssicherung

---

### **2. Profile & Modi**
- Profile: `harmonic`, `analytical`, `deep`, `philosophical`
- Moduserkennung (Coding, Coaching, Kreativ, Debug)
- Zeit‑ & Laufzeitbewusstsein (`/zeit`)

---

### **3. Ethik & Alignment**
- Maat Alignment Kernel  
- Emotion Engine & emotionale Modulation  
- Identity‑Drift‑Überwachung  
- Self‑Evolution Engine (`/evo`)

---

### **4. Gedächtnis‑System**
- SQLite Memory für Kurzzeit
- Episodisches Gedächtnis (Chat‑Ereignisse)
- Semantisches Gedächtnis (Fakten, Wissen)
- BrainMemory: Fusion aller Gedächtnisse
- LongTermMemory mit Verstärkung & Verblassen
- Dreaming‑Modus (`/dream`)

---

### **5. GUI (PySide6)**
- Chat Interface  
- Dark/Light‑Mode  
- Auto‑Scroll  
- Status‑Bubbles für Emotion, Maat‑Score, Intuition  
- Start über:  
  ```bash
  python3 maat_gui.py
  ```

---

### **6. Plugins**
- Modular über `plugins/`
- Beispiele: Speech, Websearch, Memory‑Tools
- Eigene Plugins einfach erweiterbar

---

### **7. Wichtige Befehle**
```
/hilfe
/model
/profile harmonic
/memory show | search | clear
/sem add | search | latest
/dream
/evo | /evo log
/quest start
/game
/perfinfo
```

---

## 🛠 Installation
```bash
pip install -r requirements-macarm.txt
python3 MAAT-KI.py
```

---

## 📜 Lizenz
Dieses Projekt steht unter der  
**GNU Affero General Public License v3.0 (AGPL‑3.0)**.

