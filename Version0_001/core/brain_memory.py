class BrainMemory:
    """
    Fusioniert episodic + semantic + menschliches Gedächtnisverhalten.
    """

    def __init__(self, episodic, semantic):
        self.episodic = episodic
        self.semantic = semantic

    # -------------------------------------------------------------
    def store(self, role, text):
        # Episodisches Ereignis
        self.episodic.add(role, text)

        # Semantik erkennt "Wissen"
        if len(text.split()) >= 3:
            if "?" not in text:
                self.semantic.add(text)

    # -------------------------------------------------------------
    def recall(self, query, limit=8):
        eps = self.episodic.recall(query, limit)
        sem = self.semantic.search(query, limit)

        results = []

        # 1. Episodic
        for e in eps:
            results.append({
                "ts": e["ts"],
                "role": e["role"],
                "text": e["text"],
                "category": "episodic",
            })

        # 2. Semantic
        for s in sem:
            results.append({
                "ts": s["ts"],
                "role": "semantic",
                "text": s["text"],
                "category": "knowledge",
            })

        # Dubletten filtern
        seen = set()
        final = []

        for r in results:
            if r["text"] in seen:
                continue
            seen.add(r["text"])
            final.append(r)

        return final[:limit]