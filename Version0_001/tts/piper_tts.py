import json, numpy as np, onnxruntime as ort, sounddevice as sd, unicodedata

class PiperTTS:
    def __init__(self, model_path, config_path):
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.config = json.load(open(config_path, "r", encoding="utf-8"))

        pid = self.config["phoneme_id_map"]
        self.symbol_to_id = {k: v[0] for k, v in pid.items()}

        infer = self.config.get("inference", {})
        self.noise_scale = infer.get("noise_scale", 0.667)
        self.length_scale = infer.get("length_scale", 1.0)
        self.noise_w = infer.get("noise_w", 0.8)

        self.sr = self.config["audio"]["sample_rate"]

        self.buffer = ""
        self.sentence_end = (".", "!", "?")

    def text_to_phonemes(self, text):
        text = text.lower()
        text = unicodedata.normalize("NFKD", text)
        return " ".join(list(text))

    def phonemes_to_ids(self, ph):
        return np.array([self.symbol_to_id[p] for p in ph.split(" ") if p in self.symbol_to_id], dtype=np.int64)

    def synthesize(self, text):
        ph = self.text_to_phonemes(text)
        ids = self.phonemes_to_ids(ph)
        if len(ids) == 0:
            return np.zeros(1, dtype=np.float32)

        audio = self.session.run(
            ["output"],
            {
                "input": ids.reshape(1, -1),
                "input_lengths": np.array([ids.shape[0]], dtype=np.int64),
                "scales": np.array([self.noise_scale, self.length_scale, self.noise_w], dtype=np.float32)
            }
        )[0]

        return audio.flatten()

    def speak_chunk(self, text):
        audio = self.synthesize(text)
        sd.play(audio, samplerate=self.sr)
        sd.wait()

