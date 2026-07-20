from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class RequirementCreate(BaseModel):
    project_id: UUID
    meeting_id: UUID
    category: str
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class RequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    meeting_id: UUID
    category: str
    title: str
    description: Optional[str]
    priority: str
    confidence_score: float
    status: str
    created_at: datetime
    updated_at: datetime


class AIQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    meeting_id: UUID
    question: str
    reason: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


class RequirementUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Optional[Literal["pending", "approved", "rejected"]] = None


class AIQuestionUpdate(BaseModel):
    status: Literal["pending", "answered", "dismissed"]


class AIAnalysisResponse(BaseModel):
    functional_requirements: list[RequirementResponse]
    non_functional_requirements: list[RequirementResponse]
    business_requirements: list[RequirementResponse]
    technical_requirements: list[RequirementResponse]
    missing_information: list[dict]
    questions: list[AIQuestionResponse]
