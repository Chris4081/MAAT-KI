# core/emo_mode_switch.py
# -*- coding: utf-8 -*-
"""Schalter für den Emotionsmodus der MAAT-KI.

Verwendung in MAAT-KI.py (am Anfang, nach den Imports):

    from core.emo_mode_switch import select_emo_mode

    EMO_MODE = select_emo_mode()

Danach kann EMO_MODE im Alignment-Kernel, Identity-Kernel,
Systemprompt usw. verwendet werden, um den Emotionsmodus
ein- oder auszuschalten.
"""

from colorama import Fore, Style


def select_emo_mode() -> bool:
    """Fragt beim Start, ob der Emotionsmodus aktiviert werden soll.

    Rückgabewert:
        True  -> Emotionsmodus AN (ethische Emotionen werden simuliert)
        False -> Emotionsmodus AUS (Standardmodus)
    """

    print(Fore.CYAN + "\n🌿 MAAT-KI – Startmodus auswählen:\n" + Style.RESET_ALL)
    print("1) Standardmodus (Emotionen AUS)")
    print("2) Emotionsmodus (ethische Simulation AKTIV)\n")

    choice = input("Bitte Modus wählen [1/2]: ").strip()

    if choice == "2":
        emo_mode = True
        print(
            Fore.MAGENTA
            + "💠 Emotionsmodus AKTIV: MAAT-KI simuliert jetzt ethische Emotionen.\n"
            + Style.RESET_ALL
        )
    else:
        emo_mode = False
        print(
            Fore.GREEN
            + "🌿 Standardmodus AKTIV: Emotionen deaktiviert.\n"
            + Style.RESET_ALL
        )

    return emo_mode
