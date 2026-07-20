from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session): self.db = db
    def create(self, payload: dict) -> Document:
        item = Document(**payload); self.db.add(item); self.db.flush(); return item
    def list_project(self, project_id: UUID) -> list[Document]:
        return self.db.query(Document).filter(Document.project_id == project_id).order_by(Document.document_type, Document.version.desc()).all()
    def get(self, document_id: UUID) -> Document | None: return self.db.query(Document).filter(Document.id == document_id).first()
    def next_version(self, meeting_id: UUID, document_type: str) -> int:
        return int(self.db.query(func.max(Document.version)).filter(Document.meeting_id == meeting_id, Document.document_type == document_type).scalar() or 0) + 1
    def delete(self, item: Document) -> None: self.db.delete(item)
