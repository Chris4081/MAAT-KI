# memory_backup.py
# MAAT-KI Backup Engine v1.0

import shutil
import os
from datetime import datetime

class MemoryBackup:

    def __init__(self, db_path, backup_dir):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)

    def daily_backup(self):
        today = datetime.now().strftime("%Y-%m-%d")
        backup_path = os.path.join(self.backup_dir, f"ltm_{today}.sqlite")

        if not os.path.exists(backup_path):
            shutil.copy2(self.db_path, backup_path)
            return f"Backup created: {backup_path}"
        return "Backup already exists today."