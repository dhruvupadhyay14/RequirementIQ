import uuid
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.document import Document
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.meeting import Meeting
from app.models.project import Project
from app.models.requirement import AIQuestion, Requirement
from app.rag.chunking_service import ChunkingService
from app.rag.embedding_service import EmbeddingService
from app.rag.retrieval_service import RetrievalService
from app.rag.vector_store import VectorStore

class KnowledgeService:
    def __init__(self, db: Session, chunker: ChunkingService | None = None, embeddings: EmbeddingService | None = None, store: VectorStore | None = None):
        self.db, self.chunker, self.embeddings = db, chunker or ChunkingService(), embeddings or EmbeddingService()
        self.store = store or VectorStore(settings.CHROMA_HOST, settings.CHROMA_COLLECTION)
        self.retrieval = RetrievalService(self.embeddings, self.store)
    def index_meeting(self, meeting_id: UUID, company_id: UUID) -> int:
        meeting = self._meeting(meeting_id, company_id); existing = self.db.query(KnowledgeChunk).filter(KnowledgeChunk.meeting_id == meeting_id).all(); self.store.delete([item.embedding_id for item in existing]); self.db.query(KnowledgeChunk).filter(KnowledgeChunk.meeting_id == meeting_id).delete(synchronize_session=False)
        sources = self._sources(meeting)
        entries = [(source_type, chunk) for source_type, text in sources for chunk in self.chunker.chunk(text)]
        if not entries: raise HTTPException(status_code=422, detail="No meeting knowledge is available to index")
        ids = [str(uuid.uuid4()) for _ in entries]; metadata = [{"project_id": str(meeting.project_id), "meeting_id": str(meeting.id), "source_type": source_type} for source_type, _ in entries]
        self.store.upsert(ids, self.embeddings.embed([text for _, text in entries]), [text for _, text in entries], metadata)
        for identifier, (source_type, text), item_metadata in zip(ids, entries, metadata): self.db.add(KnowledgeChunk(project_id=meeting.project_id, meeting_id=meeting.id, source_type=source_type, chunk_text=text, embedding_id=identifier, metadata_=item_metadata))
        self.db.commit(); return len(entries)
    def search(self, project_id: UUID, company_id: UUID, query: str, limit: int = 5) -> list[dict]:
        self._project(project_id, company_id); return self.retrieval.search(project_id, query, limit)
    def context(self, project_id: UUID, query: str) -> str: return self.retrieval.context(project_id, query)
    def project_memory(self, project_id: UUID, company_id: UUID) -> dict:
        project = self._project(project_id, company_id); chunks = self.db.query(KnowledgeChunk).filter(KnowledgeChunk.project_id == project_id).order_by(KnowledgeChunk.created_at.desc()).all()
        buckets: dict[str, list[str]] = {}
        for item in chunks: buckets.setdefault(item.source_type, []).append(item.chunk_text)
        return {"project_id": project_id, "project_name": project.title, "chunk_count": len(chunks), "memory": {source: values[:5] for source, values in buckets.items()}}
    def _sources(self, meeting: Meeting) -> list[tuple[str, str]]:
        transcript = "\n".join(record.transcript for record in meeting.conference_records if record.transcript)
        sources = [("project_summary", f"Project: {meeting.project.title}. {meeting.project.description or ''}"), ("meeting_transcript", transcript or meeting.description or meeting.agenda or "")]
        sources += [("requirement", f"{item.title}: {item.description or ''}") for item in self.db.query(Requirement).filter(Requirement.meeting_id == meeting.id).all()]
        sources += [("question", item.question) for item in self.db.query(AIQuestion).filter(AIQuestion.meeting_id == meeting.id, AIQuestion.status == "answered").all()]
        sources += [("document", f"{item.title}\n{item.content}") for item in self.db.query(Document).filter(Document.meeting_id == meeting.id).all()]
        return [(kind, text) for kind, text in sources if text.strip()]
    def _meeting(self, meeting_id: UUID, company_id: UUID) -> Meeting:
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting or meeting.project.company_id != company_id: raise HTTPException(status_code=404, detail="Meeting not found")
        return meeting
    def _project(self, project_id: UUID, company_id: UUID) -> Project:
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project or project.company_id != company_id: raise HTTPException(status_code=404, detail="Project not found")
        return project
