from app.events.event_types import EventType


def handle_project_created(payload: dict) -> None:
    pass


def handle_project_updated(payload: dict) -> None:
    pass


event_subscriptions = [
    (EventType.PROJECT_CREATED, handle_project_created),
    (EventType.PROJECT_UPDATED, handle_project_updated),
]
