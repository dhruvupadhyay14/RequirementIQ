import math
from urllib.parse import urlparse

class VectorStore:
    _memory: dict[str, dict] = {}
    def __init__(self, host: str | None = None, collection_name: str = "requirementiq_knowledge"):
        self.collection_name, self.collection = collection_name, None
        if host:
            try:
                import chromadb
                parsed = urlparse(host); self.collection = chromadb.HttpClient(host=parsed.hostname or host, port=parsed.port or 8000).get_or_create_collection(collection_name)
            except Exception: self.collection = None
    def upsert(self, ids: list[str], embeddings: list[list[float]], documents: list[str], metadatas: list[dict]) -> None:
        if self.collection: self.collection.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas); return
        for identifier, embedding, document, metadata in zip(ids, embeddings, documents, metadatas): self._memory[identifier] = {"embedding": embedding, "document": document, "metadata": metadata}
    def delete(self, ids: list[str]) -> None:
        if not ids: return
        if self.collection: self.collection.delete(ids=ids); return
        for identifier in ids: self._memory.pop(identifier, None)
    def query(self, embedding: list[float], project_id: str, limit: int = 5) -> list[dict]:
        if self.collection:
            result = self.collection.query(query_embeddings=[embedding], n_results=limit, where={"project_id": project_id}, include=["documents", "metadatas", "distances"])
            return [{"text": text, "metadata": metadata, "score": 1 - distance} for text, metadata, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])]
        candidates = []
        for item in self._memory.values():
            if item["metadata"].get("project_id") == project_id: candidates.append({"text": item["document"], "metadata": item["metadata"], "score": sum(a*b for a,b in zip(embedding, item["embedding"]))})
        return sorted(candidates, key=lambda item: item["score"], reverse=True)[:limit]
