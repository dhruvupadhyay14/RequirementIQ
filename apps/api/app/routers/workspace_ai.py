import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.database import get_db
from app.dependencies.auth import get_current_company_id, get_current_user
from app.models.project import Project
from app.models.user import User, UserRole
from app.models.workspace_ai import WorkspaceDocument
from app.rag.chunking_service import ChunkingService
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore
from app.schemas.workspace_ai import PlaybookCreate, PlaybookResponse, WorkspaceDocumentResponse, WorkspaceMemoryResponse
from app.workspace_ai.document_processor import DocumentProcessor
from app.workspace_ai.memory_service import MemoryService
from app.workspace_ai.playbook_service import PlaybookService

workspace_router = APIRouter(prefix="/workspace", tags=["workspace-intelligence"])
playbook_router = APIRouter(prefix="/playbooks", tags=["workspace-intelligence"])
def editor(user: User):
    if user.role == UserRole.VIEWER: raise HTTPException(status_code=403, detail="Workspace edit permissions required")
@workspace_router.post("/upload", response_model=WorkspaceDocumentResponse)
async def upload(file: UploadFile = File(...), project_id: uuid.UUID | None = Form(None), meeting_id: uuid.UUID | None = Form(None), db: Session = Depends(get_db), user: User = Depends(get_current_user), company_id: uuid.UUID = Depends(get_current_company_id)):
    editor(user)
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project or project.company_id != company_id: raise HTTPException(status_code=404, detail="Project not found")
    try: text = DocumentProcessor().extract(file.filename or "upload.txt", await file.read())
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc))
    if not text: raise HTTPException(status_code=422, detail="The uploaded document has no extractable text")
    item = WorkspaceDocument(workspace_id=user.workspace_id, project_id=project_id, meeting_id=meeting_id, file_name=file.filename or "upload", content_type=file.content_type or "application/octet-stream", extracted_text=text, created_by=user.id); db.add(item); db.flush()
    chunks = ChunkingService().chunk(text); ids = [str(uuid.uuid4()) for _ in chunks]; metadata = [{"workspace_id": str(user.workspace_id), "source_type": "workspace_document", "document_id": str(item.id)} for _ in chunks]
    VectorStore(settings.CHROMA_HOST, settings.CHROMA_COLLECTION).upsert(ids, EmbeddingService().embed(chunks), chunks, metadata); db.commit(); db.refresh(item); return item
@workspace_router.get("/memory", response_model=list[WorkspaceMemoryResponse])
def memory(db: Session = Depends(get_db), user: User = Depends(get_current_user)): return MemoryService(db).list(user.workspace_id)
@workspace_router.get("/documents", response_model=list[WorkspaceDocumentResponse])
def documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)): return db.query(WorkspaceDocument).filter(WorkspaceDocument.workspace_id == user.workspace_id).order_by(WorkspaceDocument.created_at.desc()).all()
@playbook_router.get("", response_model=list[PlaybookResponse])
def list_playbooks(db: Session = Depends(get_db), user: User = Depends(get_current_user)): return PlaybookService(db).list(user.workspace_id)
@playbook_router.post("", response_model=PlaybookResponse)
def create_playbook(body: PlaybookCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    editor(user); return PlaybookService(db).create(user.workspace_id, user.id, body.model_dump())
@playbook_router.post("/{playbook_id}/apply/{meeting_id}")
def apply_playbook(playbook_id: uuid.UUID, meeting_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user), company_id: uuid.UUID = Depends(get_current_company_id)):
    editor(user); applied = PlaybookService(db).apply(playbook_id, meeting_id, user.workspace_id, company_id); return {"applied_questions": applied}
