from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.events.event_bus import event_bus
from app.events.event_types import EventType
from app.repositories.google_repository import GoogleRepository
from app.repositories.meeting_repository import MeetingRepository
from app.services.google_oauth_service import GoogleOAuthService
from app.schemas.google import ConferenceRecordResponse
from app.models.meeting import MeetingStatus


class GoogleConferenceService:
    def __init__(self, db: Session):
        self.db = db
        self.google_repository = GoogleRepository(db)
        self.meeting_repository = MeetingRepository(db)
        self.oauth_service = GoogleOAuthService(db)

    def sync_meeting_conference(self, meeting_id: UUID, company_id: UUID) -> ConferenceRecordResponse:
        meeting = self.meeting_repository.get_meeting_by_id(meeting_id)
        if not meeting or meeting.project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

        google_account = self.google_repository.get_active_google_account(company_id)
        if not google_account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active Google account configured for this company")

        if google_account.token_expiry and google_account.token_expiry < datetime.now(timezone.utc):
            account = self.oauth_service.refresh_tokens(google_account)
            if not account:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to refresh Google access token")
            google_account = account

        record = self._sync_event_for_meeting(meeting, google_account)
        self.db.commit()
        event_bus.publish(
            EventType.GOOGLE_CONFERENCE_SYNCED,
            {
                "company_id": str(company_id),
                "meeting_id": str(meeting_id),
                "provider_conference_id": str(record.provider_conference_id),
            },
        )
        return ConferenceRecordResponse.model_validate(record)

    def get_conference_record(self, meeting_id: UUID, company_id: UUID) -> ConferenceRecordResponse:
        meeting = self.meeting_repository.get_meeting_by_id(meeting_id)
        if not meeting or meeting.project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

        record = self.google_repository.get_conference_record_by_meeting_id(meeting_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference record not found")
        return ConferenceRecordResponse.model_validate(record)

    def _sync_event_for_meeting(self, meeting, google_account):
        query_text = meeting.meeting_link or meeting.title
        events = self.oauth_service.google_client.list_calendar_events(google_account.access_token, query_text).get("items", [])
        event = self._select_event(events, meeting)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Google Calendar event not found for this meeting")

        conference_link = self._extract_meet_link(event)
        start_at = self._parse_event_time(event.get("start"))
        end_at = self._parse_event_time(event.get("end"))
        transcript = event.get("description")
        smart_notes = self._build_smart_notes(event)
        provider_conference_id = event.get("id")

        if conference_link:
            meeting.provider_meeting_id = provider_conference_id
            meeting.meeting_link = conference_link
            meeting.status = MeetingStatus.LIVE if start_at and start_at <= datetime.now(timezone.utc) <= (end_at or datetime.now(timezone.utc)) else meeting.status
            self.db.add(meeting)

        record_data = {
            "meeting_id": meeting.id,
            "google_account_id": google_account.id,
            "provider_conference_id": provider_conference_id,
            "title": event.get("summary") or meeting.title,
            "description": event.get("description"),
            "meeting_link": conference_link or event.get("htmlLink"),
            "conference_start": start_at,
            "conference_end": end_at,
            "transcript": transcript,
            "smart_notes": smart_notes,
        }
        return self.google_repository.create_or_update_conference_record(record_data)

    def _select_event(self, events: list[dict], meeting) -> dict | None:
        if not events:
            return None
        if meeting.provider_meeting_id:
            for event in events:
                if event.get("id") == meeting.provider_meeting_id:
                    return event
        if meeting.meeting_link:
            for event in events:
                if self._extract_meet_link(event) == meeting.meeting_link:
                    return event
        return events[0]

    def _extract_meet_link(self, event: dict) -> str | None:
        conference_data = event.get("conferenceData", {})
        if not conference_data:
            return None
        entry_points = conference_data.get("entryPoints", [])
        for entry in entry_points:
            if entry.get("entryPointType") == "video" and entry.get("uri"):
                return entry["uri"]
        return None

    def _parse_event_time(self, time_data: dict | None):
        if not time_data:
            return None
        timestamp = time_data.get("dateTime") or time_data.get("date")
        if not timestamp:
            return None
        try:
            return datetime.fromisoformat(timestamp)
        except ValueError:
            return None

    def _build_smart_notes(self, event: dict) -> str | None:
        summary = event.get("summary") or "Google Meet"
        description = event.get("description") or ""
        attendees = event.get("attendees") or []
        attendee_emails = ", ".join([attendee.get("email", "") for attendee in attendees if attendee.get("email")])
        notes = [f"Title: {summary}"]
        if attendee_emails:
            notes.append(f"Attendees: {attendee_emails}")
        if description:
            notes.append(f"Description: {description}")
        return "\n".join(notes)
