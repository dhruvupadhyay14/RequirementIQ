from uuid import UUID
from sqlalchemy.orm import Session
from app.models.requirement import AIQuestion, Requirement


class AIRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_requirements(self, requirements: list[dict], meeting_id: UUID, project_id: UUID) -> list[Requirement]:
        saved = []
        for payload in requirements:
            requirement = Requirement(
                project_id=project_id,
                meeting_id=meeting_id,
                category=payload.get("category", "functional"),
                title=payload.get("title", "Untitled requirement"),
                description=payload.get("description"),
                priority=payload.get("priority", "medium"),
                confidence_score=payload.get("confidence_score", 0.0),
            )
            self.db.add(requirement)
            self.db.flush()
            saved.append(requirement)
        return saved

    def save_questions(self, questions: list[dict], meeting_id: UUID) -> list[AIQuestion]:
        saved = []
        for payload in questions:
            question = AIQuestion(
                meeting_id=meeting_id,
                question=payload.get("question", ""),
                reason=payload.get("reason"),
                status=payload.get("status", "pending"),
            )
            self.db.add(question)
            self.db.flush()
            saved.append(question)
        return saved

    def remove_reanalyzable_results(self, meeting_id: UUID) -> None:
        self.db.query(Requirement).filter(
            Requirement.meeting_id == meeting_id,
            Requirement.status.in_(["pending", "rejected"]),
        ).delete(synchronize_session=False)
        self.db.query(AIQuestion).filter(
            AIQuestion.meeting_id == meeting_id,
            AIQuestion.status.in_(["pending", "dismissed"]),
        ).delete(synchronize_session=False)

    def list_requirements(self, meeting_id: UUID) -> list[Requirement]:
        return self.db.query(Requirement).filter(Requirement.meeting_id == meeting_id).order_by(Requirement.created_at.asc()).all()

    def list_questions(self, meeting_id: UUID) -> list[AIQuestion]:
        return self.db.query(AIQuestion).filter(AIQuestion.meeting_id == meeting_id).order_by(AIQuestion.created_at.asc()).all()

    def update_question_status(self, question_id: UUID, status: str) -> AIQuestion:
        question = self.db.query(AIQuestion).filter(AIQuestion.id == question_id).first()
        if not question:
            raise ValueError("Question not found")
        question.status = status
        self.db.add(question)
        self.db.flush()
        return question

    def get_requirement(self, requirement_id: UUID) -> Requirement | None:
        return self.db.query(Requirement).filter(Requirement.id == requirement_id).first()

    def update_requirement(self, requirement: Requirement, changes: dict) -> Requirement:
        for field, value in changes.items():
            setattr(requirement, field, value)
        self.db.add(requirement)
        self.db.flush()
        return requirement

    def get_question(self, question_id: UUID) -> AIQuestion | None:
        return self.db.query(AIQuestion).filter(AIQuestion.id == question_id).first()
