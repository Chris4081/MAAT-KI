import json
import os

class ProfileLoader:
    """
    MAAT-KI ProfileLoader v2.0
    - Auto-detects profile directory
    - Validates JSON profiles
    - Provides safe fallback loading
    - Caches loaded profiles
    """

    def __init__(self, root_path):
        self.root = os.path.abspath(root_path)

        # Sicherstellen, dass der Pfad NIE doppelt ist:
        expected = os.path.join(self.root, "system", "profiles")

        # Falls jemand aus Versehen system/profiles/system/profiles übergibt:
        while expected.count("system/profiles/system/profiles") > 0:
            expected = expected.replace("system/profiles/system/profiles", "system/profiles")

        self.profile_dir = expected

        if not os.path.exists(self.profile_dir):
            raise FileNotFoundError(
                f"MAAT-KI Profile Directory nicht gefunden:\n{self.profile_dir}"
            )

        self.cache = {}

    # --------------------------------------------------------------
    # Liste alle verfügbaren Profile
    # --------------------------------------------------------------
    def available_profiles(self):
        profiles = []
        for file in os.listdir(self.profile_dir):
            if file.endswith(".json"):
                profiles.append(file[:-5])  # Name ohne .json
        return sorted(profiles)

    # --------------------------------------------------------------
    # Lade ein Profil sicher
    # --------------------------------------------------------------
    def load_profile(self, name):
        name = name.strip().lower()

        # Name prüfen
        if name not in self.available_profiles():
            raise FileNotFoundError(
                f"Profil '{name}' existiert nicht.\n"
                f"Vorhandene Profile: {', '.join(self.available_profiles())}"
            )

        # Cache nutzen
        if name in self.cache:
            return self.cache[name]

        path = os.path.join(self.profile_dir, f"{name}.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Fehlerhafte JSON-Syntax in Profil '{name}':\n{e}"
            )

        # Pflichtfelder prüfen
        if "systemprompt" not in data or not data["systemprompt"].strip():
            raise ValueError(
                f"Profil '{name}' enthält keinen gültigen 'systemprompt'."
            )

        # Optional: Beschreibung
        if "description" not in data:
            data["description"] = "(keine Beschreibung)"

        self.cache[name] = data
        return data

    # --------------------------------------------------------------
    # Lade hilfreiches Standardprofil
    # --------------------------------------------------------------
    def load_default(self):
        try:
            return self.load_profile("harmonic")
        except Exception:
            # Fallback auf das erste verfügbare Profil
            profiles = self.available_profiles()
            if not profiles:
                raise FileNotFoundError("Keine Profile im Profile-Ordner vorhanden.")
            print(f"⚠ Lade Fallback-Profil: {profiles[0]}")
            return self.load_profile(profiles[0])

    # --------------------------------------------------------------
    # Beschreibung eines Profils anzeigen
    # --------------------------------------------------------------
    def describe(self, name):
        profile = self.load_profile(name)
        return profile.get("description", "(keine Beschreibung)")

