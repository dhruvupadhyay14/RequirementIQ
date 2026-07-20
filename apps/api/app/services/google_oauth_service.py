from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.integrations.google_client import GoogleClient
from app.events.event_bus import event_bus
from app.events.event_types import EventType
from app.repositories.google_repository import GoogleRepository
from app.schemas.google import GoogleOAuthUrlResponse, GoogleAccountResponse


class GoogleOAuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = GoogleRepository(db)
        self.google_client = GoogleClient()
        self._state_cache: dict[str, datetime] = {}

    def generate_authorization_url(self) -> GoogleOAuthUrlResponse:
        state = str(uuid4())
        authorization_url = self.google_client.generate_authorization_url(state)
        self._state_cache[state] = datetime.now(timezone.utc) + timedelta(minutes=10)
        return GoogleOAuthUrlResponse(authorization_url=authorization_url, state=state)

    def exchange_code(self, company_id, user_id, code: str) -> GoogleAccountResponse:
        token_data = self.google_client.exchange_code_for_tokens(code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        if not access_token or not refresh_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to obtain Google OAuth tokens")

        user_info = self.google_client.get_user_info(access_token)
        google_user_id = user_info.get("sub")
        email = user_info.get("email")
        if not google_user_id or not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to verify Google user info")

        expires_at = None
        if expires_in:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))

        existing = self.repository.get_google_account_by_google_user_id(google_user_id)
        data = {
            "company_id": company_id,
            "user_id": user_id,
            "google_user_id": google_user_id,
            "email": email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_expiry": expires_at,
            "scopes": token_data.get("scope"),
            "is_active": True,
        }
        if existing:
            account = self.repository.update_google_account(existing, data)
        else:
            account = self.repository.create_google_account(data)
        self.db.commit()
        event_bus.publish(
            EventType.GOOGLE_ACCOUNT_CONNECTED,
            {
                "company_id": str(company_id),
                "user_id": str(user_id),
                "google_user_id": google_user_id,
                "email": email,
            },
        )
        return GoogleAccountResponse.model_validate(account)

    def list_accounts(self, company_id) -> list[GoogleAccountResponse]:
        accounts = self.repository.list_google_accounts(company_id)
        return [GoogleAccountResponse.model_validate(account) for account in accounts]

    def refresh_tokens(self, account) -> dict | None:
        if not account.refresh_token:
            return None
        token_data = self.google_client.refresh_access_token(account.refresh_token)
        access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in")
        if not access_token:
            return None
        updates = {"access_token": access_token}
        if expires_in:
            updates["token_expiry"] = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        if token_data.get("scope"):
            updates["scopes"] = token_data.get("scope")
        if token_data.get("refresh_token"):
            updates["refresh_token"] = token_data.get("refresh_token")
        return self.repository.update_google_account(account, updates)
