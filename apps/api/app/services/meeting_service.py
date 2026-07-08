from uuid import UUID
from fastapi import HTTPException, status
from app.repositories.meeting_repository import MeetingRepository
from app.schemas.meeting import MeetingCreate, MeetingUpdate, ParticipantCreate, MeetingProvider, MeetingStatus
from app.models.project import Project


class MeetingService:
    def __init__(self, repository: MeetingRepository):
        self.repository = repository
        self.db = repository.db

    def get_meeting(self, meeting_id: UUID, company_id: UUID):
        meeting = self.repository.get_meeting_by_id(meeting_id)
        if not meeting or meeting.project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
        return meeting

    def list_meetings(self, company_id: UUID, limit: int = 10, offset: int = 0, provider: MeetingProvider | None = None, status: MeetingStatus | None = None, project_id: UUID | None = None, search: str | None = None, sort_by: str | None = None, sort_order: str = "asc"):
        return self.repository.list_meetings(company_id, limit, offset, provider, status, project_id, search, sort_by, sort_order)

    def create_meeting(self, company_id: UUID, user_id: UUID, meeting_in: MeetingCreate):
        project = self.repository.db.query(Project).filter(Project.id == meeting_in.project_id, Project.company_id == company_id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        meeting = self.repository.create_meeting(
            {
                **meeting_in.model_dump(),
                "created_by": user_id,
                "updated_by": user_id,
            }
        )
        self.db.commit()
        return meeting

    def update_meeting(self, meeting_id: UUID, company_id: UUID, user_id: UUID, meeting_in: MeetingUpdate):
        meeting = self.get_meeting(meeting_id, company_id)
        updates = meeting_in.model_dump(exclude_none=True)
        if not updates:
            return meeting
        updates["updated_by"] = user_id
        updated = self.repository.update_meeting(meeting, updates)
        self.db.commit()
        return updated

    def delete_meeting(self, meeting_id: UUID, company_id: UUID):
        meeting = self.get_meeting(meeting_id, company_id)
        deleted = self.repository.soft_delete_meeting(meeting)
        self.db.commit()
        return deleted

    def add_participant(self, meeting_id: UUID, company_id: UUID, participant_in: ParticipantCreate):
        meeting = self.get_meeting(meeting_id, company_id)
        participant = self.repository.add_participant(
            {
                **participant_in.model_dump(),
                "meeting_id": meeting_id,
            }
        )
        self.db.commit()
        return participant

    def list_participants(self, meeting_id: UUID, company_id: UUID):
        meeting = self.get_meeting(meeting_id, company_id)
        return self.repository.list_participants(meeting.id)

    def get_participant(self, meeting_id: UUID, participant_id: UUID, company_id: UUID):
        self.get_meeting(meeting_id, company_id)
        participant = self.repository.get_participant(meeting_id, participant_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        return participant

    def delete_participant(self, meeting_id: UUID, participant_id: UUID, company_id: UUID):
        self.get_meeting(meeting_id, company_id)
        participant = self.repository.get_participant(meeting_id, participant_id)
        if not participant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
        deleted = self.repository.delete_participant(participant)
        self.db.commit()
        return deleted
