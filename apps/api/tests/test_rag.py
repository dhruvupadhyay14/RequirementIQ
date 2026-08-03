from app.rag.chunking_service import ChunkingService
from app.rag.embedding_service import EmbeddingService
from app.rag.retrieval_service import RetrievalService
from app.rag.vector_store import VectorStore

def test_chunking_preserves_all_content():
    chunks = ChunkingService(chunk_size=20, overlap=5).chunk("Authentication needs secure SSO and password reset for all users.")
    assert len(chunks) > 1 and "Authentication" in chunks[0]

def test_fallback_embedding_is_normalized_and_repeatable():
    first = EmbeddingService("fallback").embed(["authentication login"])[0]
    assert first == EmbeddingService("fallback").embed(["authentication login"])[0]
    assert round(sum(value * value for value in first), 5) == 1

def test_semantic_search_is_project_isolated():
    embeddings, store = EmbeddingService("fallback"), VectorStore()
    store.upsert(["auth", "other"], embeddings.embed(["authentication sso login", "authentication unrelated"]), ["We discussed SSO authentication.", "Other project."], [{"project_id": "project-a", "source_type": "meeting_transcript"}, {"project_id": "project-b", "source_type": "meeting_transcript"}])
    results = RetrievalService(embeddings, store).search("project-a", "Have we discussed authentication?")
    assert results[0]["text"] == "We discussed SSO authentication."

def test_context_builder_returns_relevant_chunks():
    embeddings, store = EmbeddingService("fallback"), VectorStore()
    store.upsert(["one"], embeddings.embed(["The selected payment integration is Stripe."]), ["The selected payment integration is Stripe."], [{"project_id": "p", "source_type": "requirement"}])
    assert "Stripe" in RetrievalService(embeddings, store).context("p", "Which payment integration was chosen?")
