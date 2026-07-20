from uuid import UUID
from fastapi import HTTPException, status
from app.ai.requirement_extractor import RequirementExtractor
from app.repositories.ai_repository import AIRepository
from app.models.meeting import Meeting
from app.models.conference_record import ConferenceRecord


class AIService:
    def __init__(self, repository: AIRepository, db, extractor: RequirementExtractor | None = None):
        self.repository = repository
        self.db = db
        self.extractor = extractor or RequirementExtractor()

    def analyze_meeting(self, meeting_id: UUID, company_id: UUID, transcript: str | None = None) -> dict:
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting or meeting.project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

        transcript_payload = transcript or self._get_transcript(meeting) or meeting.agenda or meeting.description or ""
        if not transcript_payload.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No meeting transcript, agenda, or description is available for analysis",
            )
        analysis = self.extractor.extract_requirements(transcript_payload)

        requirements = []
        for category_key, category_name in [
            ("functional_requirements", "functional"),
            ("non_functional_requirements", "non_functional"),
            ("business_requirements", "business"),
            ("technical_requirements", "technical"),
        ]:
            for item in analysis.get(category_key, []):
                requirements.append(
                    {
                        "category": category_name,
                        "title": item.get("title", "Untitled requirement"),
                        "description": item.get("description", ""),
                        "priority": item.get("priority", "medium"),
                        "confidence_score": item.get("confidence_score", 0.0),
                    }
                )

        self.repository.remove_reanalyzable_results(meeting.id)
        saved_requirements = self.repository.save_requirements(requirements, meeting.id, meeting.project_id)
        saved_questions = self.repository.save_questions(analysis.get("questions", []), meeting.id)
        self.db.commit()

        return {
            "functional_requirements": [item for item in saved_requirements if item.category == "functional"],
            "non_functional_requirements": [item for item in saved_requirements if item.category == "non_functional"],
            "business_requirements": [item for item in saved_requirements if item.category == "business"],
            "technical_requirements": [item for item in saved_requirements if item.category == "technical"],
            "missing_information": analysis.get("missing_information", []),
            "questions": saved_questions,
        }

    def list_questions(self, meeting_id: UUID, company_id: UUID) -> list:
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting or meeting.project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
        return self.repository.list_questions(meeting_id)

    def list_requirements(self, meeting_id: UUID, company_id: UUID) -> list:
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting or meeting.project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
        return self.repository.list_requirements(meeting_id)

    def mark_question_answered(self, question_id: UUID, company_id: UUID) -> object:
        question = self._get_owned_question(question_id, company_id)
        question = self.repository.update_question_status(question.id, "answered")
        self.db.commit()
        return question

    def update_question(self, question_id: UUID, company_id: UUID, status_value: str):
        question = self._get_owned_question(question_id, company_id)
        updated = self.repository.update_question_status(question.id, status_value)
        self.db.commit()
        return updated

    def update_requirement(self, requirement_id: UUID, company_id: UUID, changes: dict):
        requirement = self.repository.get_requirement(requirement_id)
        if not requirement or requirement.project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
        updated = self.repository.update_requirement(requirement, changes)
        self.db.commit()
        return updated

    def _get_owned_question(self, question_id: UUID, company_id: UUID):
        question = self.repository.get_question(question_id)
        if not question or question.meeting.project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        return question

    @staticmethod
    def _get_transcript(meeting: Meeting) -> str | None:
        records = sorted(meeting.conference_records, key=lambda item: item.updated_at, reverse=True)
        for record in records:
            if record.transcript and record.transcript.strip():
                return record.transcript
        return None
