from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.meeting import Meeting
from app.models.requirement import AIQuestion
from app.models.workspace_ai import Playbook, PlaybookQuestion

class PlaybookService:
    def __init__(self, db: Session): self.db = db
    def list(self, workspace_id: UUID): return self.db.query(Playbook).filter(Playbook.workspace_id == workspace_id).all()
    def create(self, workspace_id: UUID, user_id: UUID, payload: dict):
        questions = payload.pop("questions", []); item = Playbook(workspace_id=workspace_id, created_by=user_id, **payload); self.db.add(item); self.db.flush()
        for question in questions: self.db.add(PlaybookQuestion(playbook_id=item.id, question=question["question"], reason=question.get("reason")))
        self.db.commit(); self.db.refresh(item); return item
    def apply(self, playbook_id: UUID, meeting_id: UUID, workspace_id: UUID, company_id: UUID) -> int:
        playbook = self.db.query(Playbook).filter(Playbook.id == playbook_id, Playbook.workspace_id == workspace_id).first(); meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not playbook or not meeting or meeting.project.company_id != company_id: raise HTTPException(status_code=404, detail="Playbook or meeting not found")
        questions = self.db.query(PlaybookQuestion).filter(PlaybookQuestion.playbook_id == playbook.id).all()
        for question in questions: self.db.add(AIQuestion(meeting_id=meeting_id, question=question.question, reason=question.reason or f"Suggested by {playbook.name}", status="pending"))
        self.db.commit(); return len(questions)
