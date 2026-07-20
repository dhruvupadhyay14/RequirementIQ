from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.documentation.document_generator import DocumentGenerator
from app.models.meeting import Meeting
from app.models.project import Project
from app.models.requirement import AIQuestion, Requirement
from app.repositories.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, db: Session, repository: DocumentRepository | None = None, generator: DocumentGenerator | None = None):
        self.db, self.repository, self.generator = db, repository or DocumentRepository(db), generator or DocumentGenerator()

    def generate(self, meeting_id: UUID, company_id: UUID, user_id: UUID, document_type: str):
        meeting = self._meeting(meeting_id, company_id)
        requirements = self.db.query(Requirement).filter(Requirement.meeting_id == meeting_id, Requirement.status == "approved").all()
        questions = self.db.query(AIQuestion).filter(AIQuestion.meeting_id == meeting_id).all()
        transcript = next((record.transcript for record in sorted(meeting.conference_records, key=lambda r: r.updated_at, reverse=True) if record.transcript), None)
        title, content = self.generator.generate(document_type, {"project": meeting.project, "meeting": meeting, "requirements": requirements, "questions": questions, "participants": meeting.participants, "transcript": transcript})
        item = self.repository.create({"project_id": meeting.project_id, "meeting_id": meeting_id, "document_type": document_type, "title": title, "content": content, "version": self.repository.next_version(meeting_id, document_type), "status": "draft", "created_by": user_id})
        self.db.commit(); self.db.refresh(item); return item

    def list_project(self, project_id: UUID, company_id: UUID):
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project or project.company_id != company_id: raise HTTPException(status_code=404, detail="Project not found")
        return self.repository.list_project(project_id)

    def get(self, document_id: UUID, company_id: UUID): return self._document(document_id, company_id)
    def update(self, document_id: UUID, company_id: UUID, changes: dict):
        item = self._document(document_id, company_id)
        for field, value in changes.items(): setattr(item, field, value)
        self.db.commit(); self.db.refresh(item); return item
    def delete(self, document_id: UUID, company_id: UUID):
        self.repository.delete(self._document(document_id, company_id)); self.db.commit()
    def export(self, document_id: UUID, company_id: UUID, format_name: str):
        from app.documentation.export_service import ExportService
        item = self._document(document_id, company_id); return ExportService().export(format_name, item.title, item.content)
    def _meeting(self, meeting_id: UUID, company_id: UUID):
        item = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not item or item.project.company_id != company_id: raise HTTPException(status_code=404, detail="Meeting not found")
        return item
    def _document(self, document_id: UUID, company_id: UUID):
        item = self.repository.get(document_id)
        if not item or item.project.company_id != company_id: raise HTTPException(status_code=404, detail="Document not found")
        return item
