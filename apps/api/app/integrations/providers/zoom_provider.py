from app.integrations.providers.meeting_provider import MeetingProvider


class ZoomProvider:
    provider_name = "ZOOM"

    def create_meeting(self, data: dict) -> dict:
        raise NotImplementedError("Zoom provider is a placeholder")

    def update_meeting(self, provider_meeting_id: str, data: dict) -> dict:
        raise NotImplementedError("Zoom provider is a placeholder")

    def cancel_meeting(self, provider_meeting_id: str) -> dict:
        raise NotImplementedError("Zoom provider is a placeholder")

    def get_meeting(self, provider_meeting_id: str) -> dict:
        raise NotImplementedError("Zoom provider is a placeholder")
