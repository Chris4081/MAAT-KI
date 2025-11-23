#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAAT-KI Chat GUI v4 (PySide6)
- echtes ChatGPT-Desktop-Feeling
- MAAT-KI.py bleibt unverändert (läuft als Subprozess)
- ANSI-Codes werden entfernt (kein 0m-Müll)
- Auto-Scroll auch beim Nachstreamen
- Antwort-Bubbles + kleine Status-Bubbles (Maat-Logs nebeneinander)
- Dark/Light Mode
"""

import sys
import os
import threading
import subprocess
import re
import pty

from PySide6.QtCore import Qt, QObject, Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QScrollArea,
    QFrame,
)
from PySide6.QtGui import QPalette, QColor, QFont

# =====================================================
# ANSI CLEANER
# =====================================================

# Standard-ANSI-Escape-Sequenzen (inkl. Colorama)
ANSI_RE = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")


def clean_ansi(text: str) -> str:
    # Escape-Sequenzen raus, aber Spaces & Zeilenumbrüche behalten
    txt = ANSI_RE.sub("", text)
    txt = txt.replace("\x00", "")
    # Carriage Returns in normale Newlines umwandeln
    txt = txt.replace("\r\n", "\n").replace("\r", "\n")
    return txt


# =====================================================
# MAAT-KI Subprozess via PTY (echtes Terminal)
# =====================================================

class MaatProcess(QObject):
    output_chunk = Signal(str)
    process_closed = Signal(int)

    def __init__(self, script_name="MAAT-KI.py"):
        super().__init__()
        self.script_name = script_name
        self.proc = None
        self.master = None
        self.slave = None
        self._stop = False

    def start(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, self.script_name)

        if not os.path.exists(path):
            self.output_chunk.emit(f"❌ Fehler: {path} nicht gefunden.\n")
            return

        # PTY → simuliert ein echtes Terminal (für input())
        self.master, self.slave = pty.openpty()

        try:
            self.proc = subprocess.Popen(
                ["python3", path],
                stdin=self.slave,
                stdout=self.slave,
                stderr=subprocess.STDOUT,
                text=False,  # raw bytes
                bufsize=0,
            )
        except Exception as e:
            self.output_chunk.emit(f"🚨 Startfehler: {e}\n")
            return

        threading.Thread(target=self._read_loop, daemon=True).start()

    def _read_loop(self):
        try:
            while not self._stop and self.proc.poll() is None:
                try:
                    raw = os.read(self.master, 2048)
                except OSError:
                    break

                if not raw:
                    break

                text = clean_ansi(raw.decode(errors="ignore"))
                if text:
                    self.output_chunk.emit(text)
        finally:
            if self.proc:
                self.process_closed.emit(self.proc.poll() or 0)

    def send(self, text: str):
        if not self.proc or self.proc.poll():
            self.output_chunk.emit("⚠️ MAAT-KI wurde beendet.\n")
            return

        os.write(self.master, (text + "\n").encode())

    def stop(self):
        self._stop = True
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
        except Exception:
            pass


# =====================================================
# Chat Bubbles
# =====================================================

class ChatBubble(QFrame):
    def __init__(self, text: str, is_user: bool, kind: str = "normal"):
        super().__init__()

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        # etwas größere Schrift
        base_font = QFont("Segoe UI Variable Display", 0)
        base_font.setPointSize(16 if kind == "normal" else 13)
        self.label.setFont(base_font)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.addWidget(self.label)

        if kind == "status":
            self.setObjectName("bubbleStatus")
        else:
            self.setObjectName("bubbleUser" if is_user else "bubbleMaat")

    def append_text(self, txt: str):
        self.label.setText(self.label.text() + txt)


# =====================================================
# MAIN WINDOW
# =====================================================

STATUS_KEYS = (
    "🌿 Maat-Score",
    "🌀 EMM-Maat-Vektor",
    "💙 Emotion",
    "🔮 Intuition",
    "🌿 Resonanz",
    "🜂 B_KI",
    "🔶 Identity-Drift",
    "[LAUFZEIT-GEFÜHL]",
)


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🌿 MAAT-KI Chat")
        self.resize(950, 760)

        self.dark_mode = True
        self.last_sender = None
        self.current_maat_bubble = None
        self.current_status_row = None  # ← neu: hält aktuelle Status-Zeilen-Row

        # Subprozess
        self.maat = MaatProcess()
        self.maat.output_chunk.connect(self.on_process_output)
        self.maat.process_closed.connect(self.on_process_closed)

        self.build_ui()
        self.apply_theme()

        self.maat.start()

    # -------------------------------------------------------------
    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Header
        top = QFrame()
        toplay = QHBoxLayout(top)
        toplay.setContentsMargins(18, 12, 18, 12)

        self.title = QLabel("🌿 MAAT-KI")
        title_font = QFont("Segoe UI Variable Display", 0)
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title.setFont(title_font)

        self.mode_btn = QPushButton("Light")
        self.mode_btn.setFixedWidth(80)
        self.mode_btn.clicked.connect(self.toggle_theme)

        toplay.addWidget(self.title)
        toplay.addStretch()
        toplay.addWidget(self.mode_btn)

        main.addWidget(top)

        # Scrollbereich
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.msg_container = QWidget()
        self.msg_layout = QVBoxLayout(self.msg_container)
        self.msg_layout.setSpacing(12)
        self.msg_layout.addStretch()

        # Chat-Spalte zentrieren (wie ChatGPT)
        self.msg_container.setMaximumWidth(840)
        self.scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.scroll.setWidget(self.msg_container)
        main.addWidget(self.scroll, 1)

        # Input-Bar unten
        bottom = QFrame()
        blay = QHBoxLayout(bottom)
        blay.setContentsMargins(18, 12, 18, 12)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Nachricht an MAAT-KI eingeben…")
        self.input.returnPressed.connect(self.send_message)

        send_button = QPushButton("Senden")
        send_button.clicked.connect(self.send_message)

        blay.addWidget(self.input, 1)
        blay.addWidget(send_button)

        main.addWidget(bottom)

    # -------------------------------------------------------------
    def apply_theme(self):
        if self.dark_mode:
            bg = "#0D1117"
            txt = "#E6EDF3"
            bubble_user = "#238636"
            bubble_maat = "#161B22"
            bubble_status = "#111827"
            border = "#30363D"
        else:
            bg = "#FFFFFF"
            txt = "#111827"
            bubble_user = "#3B82F6"
            bubble_maat = "#F1F5F9"
            bubble_status = "#E5E7EB"
            border = "#D1D5DB"

        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(bg))
        pal.setColor(QPalette.WindowText, QColor(txt))
        pal.setColor(QPalette.Base, QColor(bg))
        pal.setColor(QPalette.Text, QColor(txt))
        self.setPalette(pal)

        # Styles
        self.setStyleSheet(
            f"""
        QMainWindow {{
            background: {bg};
            color: {txt};
        }}
        QLabel {{
            color: {txt};
        }}
        #bubbleUser {{
            background: {bubble_user};
            border-radius: 18px;
            color: white;
            border: 1px solid {border};
        }}
        #bubbleMaat {{
            background: {bubble_maat};
            border-radius: 18px;
            color: {txt};
            border: 1px solid {border};
        }}
        #bubbleStatus {{
            background: {bubble_status};
            border-radius: 14px;
            color: {txt};
            border: 1px dashed {border};
        }}
        QLineEdit {{
            background: {bubble_maat};
            color: {txt};
            border-radius: 12px;
            border: 1px solid {border};
            padding: 12px;
            font-size: 14pt;
        }}
        QPushButton {{
            background: #10B981;
            color: white;
            border-radius: 10px;
            padding: 10px 18px;
            font-size: 13pt;
        }}
        QPushButton:hover {{
            background: #0EA271;
        }}
        """
        )

        self.mode_btn.setText("Dark" if not self.dark_mode else "Light")

    # -------------------------------------------------------------
    @Slot()
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    # -------------------------------------------------------------
    def scroll_down(self):
        QTimer.singleShot(
            30,
            lambda: self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().maximum()
            ),
        )

    def add_bubble(self, text: str, is_user: bool, kind: str = "normal"):
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        bubble = ChatBubble(text, is_user, kind=kind)

        if kind == "status":
            # Status-Bubbles werden über add_status_bubble verwaltet
            row.addStretch()
            row.addWidget(bubble)
            row.addStretch()
        else:
            if is_user:
                row.addStretch()
                row.addWidget(bubble)
            else:
                row.addWidget(bubble)
                row.addStretch()
                # neue MAAT-Antwort → neue Status-Gruppe
                self.current_status_row = None

        self.msg_layout.insertLayout(self.msg_layout.count() - 1, row)
        self.scroll_down()
        return bubble

    def add_status_bubble(self, text: str):
        text = text.strip()
        if not text:
            return

        # Status-Bubbles als kleine Chips nebeneinander in EINER Zeile
        if self.current_status_row is None:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            # links & rechts Stretch → zentriert
            row.addStretch()
            self.msg_layout.insertLayout(self.msg_layout.count() - 1, row)
            self.current_status_row = row

        bubble = ChatBubble(text, is_user=False, kind="status")
        # vor dem rechten Stretch einfügen
        idx = self.current_status_row.count()
        if idx > 0:
            idx -= 1
        self.current_status_row.insertWidget(idx, bubble)

        self.scroll_down()

    # -------------------------------------------------------------
    @Slot()
    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return

        self.add_bubble(text, True)
        self.last_sender = "user"
        self.current_status_row = None  # neue User-Eingabe → neue Status-Gruppe
        self.maat.send(text)
        self.input.clear()

    # -------------------------------------------------------------
    @Slot(str)
    def on_process_output(self, chunk: str):
        if not chunk:
            return

        # Zeilenweise splitten, damit wir Status-Zeilen abfangen können
        lines = chunk.split("\n")
        normal_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                normal_lines.append(line)
                continue

            if any(key in stripped for key in STATUS_KEYS):
                # Zeile als Status-Bubble anzeigen
                self.add_status_bubble(stripped)
            else:
                normal_lines.append(line)

        text_for_main = "\n".join(normal_lines)
        # Nur wenn wirklich Text übrig bleibt
        if not text_for_main.strip():
            return

        if self.last_sender == "maat" and self.current_maat_bubble:
            self.current_maat_bubble.append_text(text_for_main)
        else:
            self.current_maat_bubble = self.add_bubble(text_for_main, False)
            self.last_sender = "maat"

        # Auto-Scroll auch beim Nachstreamen
        self.scroll_down()

    # -------------------------------------------------------------
    @Slot(int)
    def on_process_closed(self, code: int):
        self.add_status_bubble(f"⚠️ MAAT-KI beendet (Code {code})")

    def closeEvent(self, event):
        self.maat.stop()
        super().closeEvent(event)


# =====================================================
# main()
# =====================================================

def main():
    app = QApplication(sys.argv)
    win = ChatWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()