from uuid import UUID
from sqlalchemy.orm import Session
from app.models.google_account import GoogleAccount
from app.models.conference_record import ConferenceRecord


class GoogleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_google_account_by_google_user_id(self, google_user_id: str) -> GoogleAccount | None:
        return self.db.query(GoogleAccount).filter(GoogleAccount.google_user_id == google_user_id).first()

    def get_active_google_account(self, company_id: UUID) -> GoogleAccount | None:
        return (
            self.db.query(GoogleAccount)
            .filter(GoogleAccount.company_id == company_id, GoogleAccount.is_active.is_(True))
            .first()
        )

    def list_google_accounts(self, company_id: UUID) -> list[GoogleAccount]:
        return self.db.query(GoogleAccount).filter(GoogleAccount.company_id == company_id, GoogleAccount.deleted_at.is_(None)).all()

    def create_google_account(self, account_data: dict) -> GoogleAccount:
        account = GoogleAccount(**account_data)
        self.db.add(account)
        self.db.flush()
        return account

    def update_google_account(self, account: GoogleAccount, updates: dict) -> GoogleAccount:
        for key, value in updates.items():
            setattr(account, key, value)
        self.db.add(account)
        self.db.flush()
        return account

    def get_conference_record_by_meeting_id(self, meeting_id: UUID) -> ConferenceRecord | None:
        return self.db.query(ConferenceRecord).filter(ConferenceRecord.meeting_id == meeting_id).first()

    def create_or_update_conference_record(self, record_data: dict) -> ConferenceRecord:
        record = self.get_conference_record_by_meeting_id(record_data["meeting_id"])
        if record:
            for key, value in record_data.items():
                setattr(record, key, value)
            self.db.add(record)
            self.db.flush()
            return record

        record = ConferenceRecord(**record_data)
        self.db.add(record)
        self.db.flush()
        return record
