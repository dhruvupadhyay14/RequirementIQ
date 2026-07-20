from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import requests
from app.config.settings import settings


def _ensure_configured() -> None:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET or not settings.GOOGLE_REDIRECT_URI:
        raise RuntimeError("Google OAuth is not configured. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI.")


class GoogleClient:
    AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
    CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    def generate_authorization_url(self, state: str) -> str:
        _ensure_configured()
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile https://www.googleapis.com/auth/calendar.events.readonly",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"{self.AUTH_BASE_URL}?{urlencode(params)}"

    def exchange_code_for_tokens(self, code: str) -> dict:
        _ensure_configured()
        response = requests.post(
            self.TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self, refresh_token: str) -> dict:
        _ensure_configured()
        response = requests.post(
            self.TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def get_user_info(self, access_token: str) -> dict:
        response = requests.get(
            self.USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def list_calendar_events(self, access_token: str, query: str, max_results: int = 10) -> dict:
        response = requests.get(
            self.CALENDAR_EVENTS_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "q": query,
                "singleEvents": "true",
                "orderBy": "startTime",
                "maxResults": max_results,
                "conferenceDataVersion": 1,
                "fields": "items(id,summary,description,htmlLink,conferenceData,start,end,attendees)",
            },
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
