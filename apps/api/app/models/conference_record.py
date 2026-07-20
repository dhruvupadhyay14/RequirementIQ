import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class ConferenceRecord(Base):
    __tablename__ = "conference_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False)
    google_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("google_accounts.id"), nullable=False)
    provider_conference_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meeting_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    conference_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    conference_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    smart_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    meeting: Mapped["Meeting"] = relationship(back_populates="conference_records")
    google_account: Mapped["GoogleAccount"] = relationship(back_populates="conference_records")
