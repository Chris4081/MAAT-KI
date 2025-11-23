# core/memory_tools.py

import re

def handle_memory_commands(user_input, memory):
    """
    Interpretiert einfache Memory-Kommandos.
    Gibt True zurück, wenn das Kommando verarbeitet wurde.
    """

    text = user_input.strip().lower()

    # ------------------------------
    # MEMORY: ALLES ZEIGEN
    # ------------------------------
    if text == "memory show":
        print("\n🧠 MEMORY – LETZTE EINTRÄGE:\n")
        ctx = memory.last_context(20)
        print(ctx if ctx else "(leer)")
        print()
        return True

    # ------------------------------
    # MEMORY LEEREN
    # ------------------------------
    if text in ["memory clear", "clear memory"]:
        print("\n🧽 MEMORY GELEERT.\n")
        memory.clear()
        return True

    # ------------------------------
    # MEMORY: N LETZTE ZEIGEN
    # ------------------------------
    match = re.match(r"memory last (\d+)", text)
    if match:
        n = int(match.group(1))
        print(f"\n🧠 MEMORY – LETZTE {n} EINTRÄGE:\n")
        ctx = memory.last_context(limit=n)
        print(ctx if ctx else "(leer)")
        print()
        return True

    # ------------------------------
    # REMEMBER: Benutzer zwingt Erinnerung
    # Beispiel: remember: Ich mag Pizza.
    # ------------------------------
    if text.startswith("remember:"):
        data = user_input[len("remember:"):].strip()
        if data:
            memory.add("forced", data)
            print(f"\n💾 Gespeichert: {data}\n")
        else:
            print("\n⚠️ Leerer remember:-Befehl.\n")
        return True

    # ------------------------------
    # FORGET: Inhalt löschen
    # Beispiel: forget: Pizza
    # ------------------------------
    if text.startswith("forget:"):
        key = user_input[len("forget:"):].strip()
        if key:
            memory.delete_matching(key)
            print(f"\n🗑️ Gelöscht: alles mit '{key}'\n")
        else:
            print("\n⚠️ Leerer forget:-Befehl.\n")
        return True

    return False
