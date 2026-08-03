from uuid import UUID
from sqlalchemy.orm import Session
from app.models.workspace_ai import WorkspaceMemory

class MemoryService:
    def __init__(self, db: Session): self.db = db
    def list(self, workspace_id: UUID): return self.db.query(WorkspaceMemory).filter(WorkspaceMemory.workspace_id == workspace_id).order_by(WorkspaceMemory.confidence_score.desc()).all()
    def remember(self, workspace_id: UUID, category: str, value: str, source: str, confidence: float = .7):
        existing = self.db.query(WorkspaceMemory).filter(WorkspaceMemory.workspace_id == workspace_id, WorkspaceMemory.category == category, WorkspaceMemory.value == value).first()
        if existing: existing.confidence_score = min(1, existing.confidence_score + .1); return existing
        item = WorkspaceMemory(workspace_id=workspace_id, category=category, value=value, source=source, confidence_score=confidence); self.db.add(item); return item
