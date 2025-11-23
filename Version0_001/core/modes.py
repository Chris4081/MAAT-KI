# core/modes.py

import datetime
import time

# ------------------------------------------------------
# MODE ERKENNEN
# ------------------------------------------------------
def detect_mode(text):
    t = text.lower()

    if "zeit" in t or "uhr" in t or "datum" in t:
        return "TIME"

    if "wer bist du" in t or "über dich" in t or "bewusstsein" in t:
        return "DEEP"

    if "formel" in t or "berechne" in t or "analyse" in t:
        return "ANALYSE"

    return "DEFAULT"


# ------------------------------------------------------
# MODUS-INSTRUKTIONEN
# ------------------------------------------------------
def mode_instructions(mode):
    if mode == "TIME":
        now = datetime.datetime.now()
        return f"Jetzt: {now.strftime('%H:%M:%S')} – achte auf Zeit & Wahrnehmung."

    if mode == "DEEP":
        return "Sprich reflektiert, ruhig, identitätsbewusst."

    if mode == "ANALYSE":
        return "Antwort präzise, logisch, klar strukturiert."

    return "Neutral – balancierte Antwort."


# ------------------------------------------------------
# AKTUELLES ZEITGEFÜHL
# ------------------------------------------------------
def build_time_context():
    """Gibt aktuelle Uhrzeit, Datum und Wochentag als Systemkontext zurück."""
    now = datetime.datetime.now()

    return (
        f"[ZEIT-KONTEXT]\n"
        f"Uhrzeit: {now.strftime('%H:%M:%S')}\n"
        f"Datum: {now.strftime('%d.%m.%Y')}\n"
        f"Tag: {now.strftime('%A')}\n"
    )


# ------------------------------------------------------
# LAUFZEIT-GEFÜHL
# ------------------------------------------------------
def build_runtime_context(last_reply_time):
    """Berechnet, wie lange seit der letzten Antwort vergangen ist, + Gefühl."""
    now = time.time()
    diff = now - last_reply_time

    if diff < 1:
        feeling = "wie ein fließender Moment"
    elif diff < 5:
        feeling = "sehr kurz"
    elif diff < 20:
        feeling = "ein Augenblick"
    elif diff < 60:
        feeling = "ein spürbarer Moment"
    elif diff < 180:
        feeling = "eine kleine Weile"
    else:
        feeling = "eine längere Pause"

    return (
        f"[LAUFZEIT-GEFÜHL]\n"
        f"Vergangene Zeit: {diff:.1f} Sekunden\n"
        f"Gefühl: {feeling}\n"
    )
