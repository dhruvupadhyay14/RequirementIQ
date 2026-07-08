from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol


class MeetingProvider(Protocol):
    provider_name: str

    def create_meeting(self, data: dict) -> dict:
        ...

    def update_meeting(self, provider_meeting_id: str, data: dict) -> dict:
        ...

    def cancel_meeting(self, provider_meeting_id: str) -> dict:
        ...

    def get_meeting(self, provider_meeting_id: str) -> dict:
        ...
