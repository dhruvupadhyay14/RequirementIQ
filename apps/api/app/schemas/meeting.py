from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from app.models.meeting import MeetingProvider, MeetingStatus


class MeetingBase(BaseModel):
    project_id: UUID
    provider: MeetingProvider = MeetingProvider.GOOGLE_MEET
    meeting_link: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    agenda: Optional[str] = None
    status: MeetingStatus = MeetingStatus.SCHEDULED
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    provider: Optional[MeetingProvider] = None
    meeting_link: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    agenda: Optional[str] = None
    status: Optional[MeetingStatus] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)


class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    provider: MeetingProvider
    provider_meeting_id: Optional[str]
    meeting_link: Optional[str]
    title: str
    description: Optional[str]
    agenda: Optional[str]
    status: MeetingStatus
    scheduled_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_minutes: Optional[int]
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class MeetingListResponse(BaseModel):
    meetings: list[MeetingResponse]
    total: int


class ParticipantBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    role: Optional[str] = None
    attendance_status: Optional[str] = None


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    meeting_id: UUID
    name: str
    email: Optional[EmailStr]
    company: Optional[str]
    role: Optional[str]
    attendance_status: Optional[str]
    joined_at: Optional[datetime]
    left_at: Optional[datetime]
