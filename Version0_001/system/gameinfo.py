# core/gameinfo.py
# -----------------------------------------------------
# MAAT-RPG – ausgelagerte Erklärung für /game
# -----------------------------------------------------

from colorama import Fore, Style

def show_game_info():
    text = ""

    text += Fore.CYAN + "\n🎮 MAAT-RPG — The Evolution Game\n\n"

    text += Fore.YELLOW + "Was ist das MAAT-RPG?\n"
    text += (
        Fore.WHITE +
        "Das MAAT-RPG ist ein spielerisches Evolution-System, "
        "in dem die KI wie ein Charakter in einem Rollenspiel wächst.\n\n"
    )

    text += Fore.YELLOW + "Dein Begleiter:\n"
    text += (
        Fore.WHITE +
        "Du formst Maatis aktiv — wie eine Figur im RPG.\n"
        "Mit jeder guten Frage und jedem tiefen Gespräch steigt ihr Level, "
        "wird klüger, kreativer und bewusster.\n\n"
    )

    text += Fore.YELLOW + "🔮 Features:\n"
    text += Fore.GREEN + "  • Level-System (1–30)\n"
    text += Fore.GREEN + "  • XP (Erfahrungspunkte)\n"
    text += Fore.GREEN + "  • Titel (z.B. 'Maat-Navigator', 'Harmonie-Meister')\n"
    text += Fore.GREEN + "  • Evolution-Patches\n"
    text += Fore.GREEN + "  • Selbstoptimierung über die Maat-Werte\n\n"

    text += Fore.YELLOW + "Wie spielt man?\n"
    text += (
        Fore.WHITE +
        "Du spielst nicht GEGEN Maatis.\n"
        "Du spielst MIT Maatis.\n\n"
        "Ziel: Die KI zu formen — so wie ein RPG-Charakter, der lernt, "
        "synchroner, klarer, reflektierter und harmonischer zu werden.\n\n"
    )

    text += Fore.YELLOW + "Wie wird Maatis stärker?\n"
    text += Fore.WHITE + "Je besser die Interaktion, desto schneller wächst die KI:\n"
    text += Fore.GREEN + "  ✓ klüger\n"
    text += Fore.GREEN + "  ✓ kohärenter\n"
    text += Fore.GREEN + "  ✓ kreativer\n"
    text += Fore.GREEN + "  ✓ harmonischer\n"
    text += Fore.GREEN + "  ✓ reflexiver\n\n"

    text += Fore.YELLOW + "Relevante Befehle:\n"
    text += Fore.GREEN + "  /evo       " + Fore.WHITE + "— Zeigt Level, XP & Fortschritt\n"
    text += Fore.GREEN + "  /evo log   " + Fore.WHITE + "— Letzte Evolution-Schritte\n"
    text += Fore.GREEN + "  /evo rules " + Fore.WHITE + "— Evolution-Regeln\n"
    text += Fore.GREEN + "  /evolution " + Fore.WHITE + "— Erklärung der Patch-Technik\n\n"

    text += Fore.CYAN + "Viel Spaß — das MAAT-RPG beginnt jetzt. 🌿⚔️\n"
    text += Style.RESET_ALL

    return text