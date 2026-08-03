import hashlib, math, os
import requests

class EmbeddingService:
    def __init__(self, provider: str | None = None): self.provider = (provider or os.getenv("EMBEDDING_PROVIDER", "fallback")).lower()
    def embed(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "openai" and os.getenv("OPENAI_API_KEY"):
            try:
                response = requests.post("https://api.openai.com/v1/embeddings", headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}, json={"model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"), "input": texts}, timeout=30); response.raise_for_status(); return [item["embedding"] for item in response.json()["data"]]
            except (requests.RequestException, KeyError, ValueError): pass
        return [self._fallback(text) for text in texts]
    @staticmethod
    def _fallback(text: str, dimensions: int = 128) -> list[float]:
        values = [0.0] * dimensions
        for token in text.lower().split(): values[int(hashlib.sha256(token.encode()).hexdigest(), 16) % dimensions] += 1.0
        norm = math.sqrt(sum(v * v for v in values)) or 1.0
        return [v / norm for v in values]
