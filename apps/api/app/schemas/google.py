from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class GoogleOAuthUrlResponse(BaseModel):
    authorization_url: str
    state: str


class GoogleAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    user_id: UUID
    google_user_id: str
    email: str
    scopes: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ConferenceRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    meeting_id: UUID
    google_account_id: UUID
    provider_conference_id: str
    title: str
    description: Optional[str]
    meeting_link: Optional[str]
    conference_start: Optional[datetime]
    conference_end: Optional[datetime]
    transcript: Optional[str]
    smart_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
