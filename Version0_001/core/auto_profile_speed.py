# core/auto_profile_speed.py

import time
import json
import os

PROFILE_PATH = "data/performance_profile.json"


class AutoProfileSpeedTrainer:

    def __init__(self):
        self.profile = self._load_profile()

    # ----------------------------------------------------
    # LOAD + SAVE
    # ----------------------------------------------------
    def _load_profile(self):
        if os.path.exists(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save(self):
        with open(PROFILE_PATH, "w") as f:
            json.dump(self.profile, f, indent=2)

    # ----------------------------------------------------
    # UPDATE after each first-token measurement
    # ----------------------------------------------------
    def update_first_token_speed(self, seconds):
        """
        seconds = gemessene Zeit zwischen Prompt und erstem Token
        """

        history = self.profile.get("first_token_history", [])
        history.append(seconds)

        # Maximal 20 Werte → genug für gleitenden Mittelwert
        history = history[-20:]

        avg = sum(history) / len(history)

        self.profile["first_token_history"] = history
        self.profile["avg_first_token"] = avg

        # Dynamischer Lern-Faktor
        if avg < 0.4:
            self.profile["performance_tier"] = "ULTRA"
        elif avg < 0.8:
            self.profile["performance_tier"] = "HIGH"
        elif avg < 1.6:
            self.profile["performance_tier"] = "MEDIUM"
        else:
            self.profile["performance_tier"] = "LOW"

        self._save()
        return avg

    # ----------------------------------------------------
    # Auto-Batch Optimizer
    # ----------------------------------------------------
    def suggest_batch_size(self):
        tier = self.profile.get("performance_tier", "MEDIUM")

        if tier == "ULTRA":
            return 1024
        if tier == "HIGH":
            return 768
        if tier == "MEDIUM":
            return 512
        return 256

    # ----------------------------------------------------
    # Auto-Thread Optimizer
    # ----------------------------------------------------
    def suggest_threads(self, cpu_cores):
        tier = self.profile.get("performance_tier", "MEDIUM")

        if tier == "ULTRA":
            return max(1, cpu_cores - 1)
        if tier == "HIGH":
            return max(1, cpu_cores - 2)
        if tier == "MEDIUM":
            return max(1, cpu_cores - 3)
        return max(1, cpu_cores - 4)

    # ----------------------------------------------------
    # Debug output
    # ----------------------------------------------------
    def pretty_info(self):
        if not self.profile:
            return "Keine Performance-Daten gespeichert."

        return (
            "📊 MAAT-KI Performance-Profil\n"
            f"- Durchschnitt erster Token: {self.profile.get('avg_first_token', '?'):.3f} Sekunden\n"
            f"- Tier: {self.profile.get('performance_tier', 'MEDIUM')}\n"
            f"- Letzte 20 Messungen: {self.profile.get('first_token_history')}\n"
        )
