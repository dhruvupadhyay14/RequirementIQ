from typing import Callable
from app.events.event_types import EventType


class EventBus:
    def __init__(self):
        self._subscribers: dict[EventType, list[Callable]] = {}

    def subscribe(self, event_type: EventType, handler: Callable):
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: EventType, payload: dict) -> None:
        for handler in self._subscribers.get(event_type, []):
            handler(payload)


event_bus = EventBus()
