#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAAT-KI — Model Downloader
--------------------------
Automatischer Download des empfohlenen Modells:

Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf
Quelle:
GPT4All-Community (HuggingFace)

⚠️ Hinweis:
Dieses Modell wird als leistungsfähig angenommen, benötigt aber
möglicherweise weitere Tests und Nutzer-Feedback.
Nur Modelle, die offiziell in der GPT4All-GUI angezeigt werden,
sind von Nomic verifiziert. Nutzung auf eigene Gefahr.
"""

import os
import shutil
import requests

MODEL_URL = (
    "https://huggingface.co/GGPT4All-Community/Meta-Llama-3.1-8B-Instruct-128k-GGUF/"
    "resolve/main/Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf?download=true"
)

MODEL_NAME = "Meta-Llama-3.1-8B-Instruct-128k-Q4_0.gguf"


def download_model():
    print("\n🌿 MAAT-KI Model Downloader")
    print("──────────────────────────────────────────────")
    print(f"📦 Modell: {MODEL_NAME}")
    print(f"🔗 Quelle: {MODEL_URL}")
    print("──────────────────────────────────────────────\n")

    root_path = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(root_path, "models")

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    target_path = os.path.join(models_dir, MODEL_NAME)
    temp_path = os.path.join(root_path, MODEL_NAME)

    # Wenn Modell schon existiert
    if os.path.exists(target_path):
        print("✔️ Modell bereits im models/ Verzeichnis vorhanden.")
        return

    print("⏳ Lade Modell herunter… (dies kann dauern)")

    with requests.get(MODEL_URL, stream=True) as r:
        r.raise_for_status()
        with open(temp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    print(f"✔️ Download abgeschlossen: {temp_path}")

    # Kopieren ins models/
    print("📁 Verschiebe Modell in das models/ Verzeichnis…")
    shutil.move(temp_path, target_path)

    print("🌟 Fertig! Modell ist bereit für MAAT-KI.")
    print(f"➡️ {target_path}")


if __name__ == "__main__":
    download_model()