# core/llm_loader.py
# MAAT-KI macOS M-Series Optimized Loader

import os
import platform
import multiprocessing
from llama_cpp import Llama


def detect_threads():
    """
    Nutzt logische CPU-Kerne, begrenzt aber auf sinnvolle Werte.
    M1/M2/M3/M4: 6–10 Threads
    Intel:       alle logischen Kerne
    """
    cores = multiprocessing.cpu_count()
    system = platform.processor().lower()

    if "apple" in system:   # M-Series
        return min(cores, 8)
    return cores


def detect_gpu_backend():
    """
    macOS: METAL
    Linux: VULKAN optional, sonst CPU
    Windows: DirectML optional
    """
    system = platform.system().lower()

    if system == "darwin":
        return "METAL"

    if system == "linux":
        return "VULKAN"

    return "CPU"


def load_llm(model_path, perf):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❗ Modell nicht gefunden: {model_path}")

    backend = detect_gpu_backend()
    threads = detect_threads()
    n_ctx = perf.get("n_ctx", 8192)

    print("────────────────────────────────────────────")
    print("🔧 MAAT-KI macOS Optimized LLM Loader")
    print("────────────────────────────────────────────")
    print(f"📦 Modell       : {model_path}")
    print(f"🧠 Backend      : {backend}")
    print(f"🧵 Threads      : {threads}")
    print(f"🧩 Kontext       : {n_ctx}")
    print("────────────────────────────────────────────\n")

    # --------------------------------------------------------
    #   WICHTIG: KEIN rope_scaling_type, KEIN rope_freq_base!!!
    #   → löst alle Apple Silicon rope-Fehler!
    # --------------------------------------------------------

    # GPU-Layer setzen
    if backend == "METAL":
        n_gpu_layers = -1
    elif backend == "VULKAN":
        n_gpu_layers = -1
    else:
        n_gpu_layers = 0

    # --------------------------------------------------------
    #   MODELL INSTANTIATION (stabil)
    # --------------------------------------------------------
    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=threads,
        n_gpu_layers=n_gpu_layers,
        use_mlock=False,
        use_mmap=True,
        verbose=False
    )

    print("🌿 Modell erfolgreich geladen unter macOS.\n")
    return llm