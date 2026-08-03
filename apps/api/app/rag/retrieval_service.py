from uuid import UUID
from app.rag.context_builder import ContextBuilder
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore

class RetrievalService:
    def __init__(self, embeddings: EmbeddingService, store: VectorStore, context_builder: ContextBuilder | None = None): self.embeddings, self.store, self.context_builder = embeddings, store, context_builder or ContextBuilder()
    def search(self, project_id: UUID, query: str, limit: int = 5) -> list[dict]: return self.store.query(self.embeddings.embed([query])[0], str(project_id), limit)
    def context(self, project_id: UUID, query: str, limit: int = 5) -> str: return self.context_builder.build(self.search(project_id, query, limit))
