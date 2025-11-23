# core/thinkloop.py

class ThinkLoop:

    def __init__(self):
        self.triggers = ["denke", "überlege", "prüfe", "analyse"]

    def needs_think(self, text):
        t = text.lower()
        return any(w in t for w in self.triggers)

    # ----------------------------------------------------------
    # UNIVERSAL COMPLETION WRAPPER — keine llama.cpp Änderung
    # ----------------------------------------------------------
    def _universal_completion(self, llm, messages):
        """
        Universeller Wrapper, der automatisch erkennt,
        welche API das Modell unterstützt.
        """

        # llama.cpp API
        if hasattr(llm, "create_chat_completion"):
            resp = llm.create_chat_completion(
                messages=messages,
                max_tokens=256,
                temperature=0.3
            )
            return resp["choices"][0]["message"]["content"]

        # OpenAI API Style
        if hasattr(llm, "chat") and hasattr(llm.chat, "completions"):
            resp = llm.chat.completions.create(
                model=llm.model,
                messages=messages,
                max_tokens=256,
                temperature=0.3
            )
            return resp.choices[0].message.content

        # Ollama Style
        if hasattr(llm, "generate"):
            text = llm.generate(
                prompt=str(messages),
                max_tokens=256,
                temperature=0.3
            )
            return text

        # Generic call
        try:
            return llm(messages)
        except:
            return "Denken war nicht möglich (unbekannte API)."

    # ----------------------------------------------------------
    # THINK LOOP
    # ----------------------------------------------------------
    def run_thinkloop(self, llm, conversation):
        messages = conversation + [{
            "role": "system",
            "content": (
                "Interner Denkmodus: "
                "Formuliere deine internen Gedanken klar, logisch und strukturiert. "
                "Gib KEINE Nutzerantwort aus."
            )
        }]

        thoughts = self._universal_completion(llm, messages)

        # Cleanup
        return thoughts.strip()
