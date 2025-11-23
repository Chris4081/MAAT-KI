# memory_fusion.py
# MAAT-KI — Memory Fusion Engine v1.0

from core.semantic_memory import SemanticMemory

class MemoryFusion:

    def __init__(self, semantic: SemanticMemory):
        self.semantic = semantic

    def fusion(self, query_terms):
        """
        Kombiniert relevante Erinnerungen in einem einzigen Erkenntnisblock.
        """
        combined = []

        for term in query_terms:
            hits = self.semantic.search(term, top_k=5)
            for h in hits:
                combined.append(h["compressed"])

        # Entferne Duplikate
        uniq = list(dict.fromkeys(combined))

        return "\n".join(f"- {u}" for u in uniq)