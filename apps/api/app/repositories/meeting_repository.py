from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from app.models.meeting import Meeting
from app.models.participant import Participant


class MeetingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_meeting_by_id(self, meeting_id: UUID) -> Meeting | None:
        return self.db.query(Meeting).filter(Meeting.id == meeting_id, Meeting.deleted_at.is_(None)).first()

    def list_meetings(self, company_id: UUID, limit: int = 10, offset: int = 0, provider: str | None = None, status: str | None = None, project_id: UUID | None = None, search: str | None = None, sort_by: str | None = None, sort_order: str = "asc") -> tuple[list[Meeting], int]:
        query = self.db.query(Meeting).join(Meeting.project).filter(Meeting.deleted_at.is_(None), Meeting.project.has(company_id=company_id))

        if provider:
            query = query.filter(Meeting.provider == provider)
        if status:
            query = query.filter(Meeting.status == status)
        if project_id:
            query = query.filter(Meeting.project_id == project_id)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Meeting.title.ilike(search_term)
                | Meeting.description.ilike(search_term)
                | Meeting.agenda.ilike(search_term)
            )

        total = query.count()

        if sort_by in {"title", "scheduled_at", "started_at", "ended_at"}:
            order_column = getattr(Meeting, sort_by)
            query = query.order_by(order_column.desc() if sort_order == "desc" else order_column.asc())
        else:
            query = query.order_by(Meeting.scheduled_at.asc())

        meetings = query.offset(offset).limit(limit).all()
        return meetings, total

    def create_meeting(self, meeting_data: dict) -> Meeting:
        meeting = Meeting(**meeting_data)
        self.db.add(meeting)
        self.db.flush()
        return meeting

    def update_meeting(self, meeting: Meeting, updates: dict) -> Meeting:
        for field, value in updates.items():
            setattr(meeting, field, value)
        self.db.add(meeting)
        self.db.flush()
        return meeting

    def soft_delete_meeting(self, meeting: Meeting) -> Meeting:
        meeting.deleted_at = func.now()
        self.db.add(meeting)
        self.db.flush()
        return meeting

    def add_participant(self, participant_data: dict) -> Participant:
        participant = Participant(**participant_data)
        self.db.add(participant)
        self.db.flush()
        return participant

    def list_participants(self, meeting_id: UUID) -> list[Participant]:
        return self.db.query(Participant).filter(Participant.meeting_id == meeting_id).all()

    def get_participant(self, meeting_id: UUID, participant_id: UUID) -> Participant | None:
        return self.db.query(Participant).filter(Participant.meeting_id == meeting_id, Participant.id == participant_id).first()

    def delete_participant(self, participant: Participant) -> Participant:
        self.db.delete(participant)
        self.db.flush()
        return participant
