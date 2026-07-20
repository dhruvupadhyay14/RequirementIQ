from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from app.dependencies.auth import get_current_user, get_current_company_id
from app.database import get_db
from app.services.google_oauth_service import GoogleOAuthService
from app.services.google_conference_service import GoogleConferenceService
from app.schemas.google import GoogleOAuthUrlResponse, GoogleAccountResponse, ConferenceRecordResponse
from app.models.user import User

router = APIRouter(prefix="/google", tags=["google"])


@router.get("/oauth/url", response_model=GoogleOAuthUrlResponse)
def get_google_oauth_url(
    db: Session = Depends(get_db),
):
    service = GoogleOAuthService(db)
    return service.generate_authorization_url()


@router.get("/oauth/callback", response_model=GoogleAccountResponse)
def google_oauth_callback(
    code: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = GoogleOAuthService(db)
    return service.exchange_code(current_user.company_id, current_user.id, code)


@router.get("/accounts", response_model=list[GoogleAccountResponse])
def list_google_accounts(
    company_id: UUID = Depends(get_current_company_id),
    db: Session = Depends(get_db),
):
    service = GoogleOAuthService(db)
    return service.list_accounts(company_id)


@router.post("/conferences/{meeting_id}/sync", response_model=ConferenceRecordResponse)
def sync_google_conference(
    meeting_id: UUID,
    company_id: UUID = Depends(get_current_company_id),
    db: Session = Depends(get_db),
):
    service = GoogleConferenceService(db)
    return service.sync_meeting_conference(meeting_id, company_id)


@router.get("/conferences/{meeting_id}", response_model=ConferenceRecordResponse)
def get_google_conference_record(
    meeting_id: UUID,
    company_id: UUID = Depends(get_current_company_id),
    db: Session = Depends(get_db),
):
    service = GoogleConferenceService(db)
    return service.get_conference_record(meeting_id, company_id)
