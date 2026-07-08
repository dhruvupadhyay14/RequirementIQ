from fastapi import APIRouter, Depends, Query, Path, status
from typing import Optional
from uuid import UUID
from app.dependencies.auth import get_current_user, get_current_company_id
from app.models.user import User
from app.repositories.meeting_repository import MeetingRepository
from app.services.meeting_service import MeetingService
from app.schemas.meeting import (
    MeetingCreate,
    MeetingResponse,
    MeetingListResponse,
    MeetingUpdate,
    ParticipantCreate,
    ParticipantResponse,
    MeetingProvider,
    MeetingStatus,
)
from app.database import get_db

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("/", response_model=MeetingListResponse)
def list_meetings(
    company_id: UUID = Depends(get_current_company_id),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    provider: Optional[MeetingProvider] = Query(None),
    status: Optional[MeetingStatus] = Query(None),
    project_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db=Depends(get_db),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    meetings, total = service.list_meetings(company_id, limit, offset, provider, status, project_id, search, sort_by, sort_order)
    return {"meetings": meetings, "total": total}


@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def create_meeting(
    meeting_in: MeetingCreate,
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
    current_user: User = Depends(get_current_user),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    meeting = service.create_meeting(company_id, current_user.id, meeting_in)
    return meeting


@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: UUID = Path(...),
    company_id: UUID = Depends(get_current_company_id),
    db=Depends(get_db),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    return service.get_meeting(meeting_id, company_id)


@router.patch("/{meeting_id}", response_model=MeetingResponse)
def update_meeting(
    meeting_id: UUID,
    meeting_in: MeetingUpdate,
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
    current_user: User = Depends(get_current_user),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    return service.update_meeting(meeting_id, company_id, current_user.id, meeting_in)


@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: UUID,
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    service.delete_meeting(meeting_id, company_id)
    return None


@router.post("/{meeting_id}/participants", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def add_participant(
    meeting_id: UUID,
    participant_in: ParticipantCreate,
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    return service.add_participant(meeting_id, company_id, participant_in)


@router.get("/{meeting_id}/participants", response_model=list[ParticipantResponse])
def list_participants(
    meeting_id: UUID,
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    return service.list_participants(meeting_id, company_id)


@router.get("/{meeting_id}/participants/{participant_id}", response_model=ParticipantResponse)
def get_participant(
    meeting_id: UUID,
    participant_id: UUID,
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    return service.get_participant(meeting_id, participant_id, company_id)


@router.delete("/{meeting_id}/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(
    meeting_id: UUID,
    participant_id: UUID,
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
):
    repository = MeetingRepository(db)
    service = MeetingService(repository)
    service.delete_participant(meeting_id, participant_id, company_id)
    return None
