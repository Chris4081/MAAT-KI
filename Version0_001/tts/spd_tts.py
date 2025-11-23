import subprocess

class SpdTTS:
    def speak_chunk(self, text):
        if not text.strip():
            return
        try:
            subprocess.call(["spd-say", "-l", "de", text])
        except FileNotFoundError:
            print("⚠️ Speech Dispatcher (spd-say) nicht installiert.")
