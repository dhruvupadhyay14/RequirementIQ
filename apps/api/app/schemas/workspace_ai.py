from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class WorkspaceMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID; category: str; value: str; confidence_score: float; source: str; updated_at: datetime
class WorkspaceDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID; file_name: str; content_type: str; status: str; created_at: datetime
class PlaybookQuestionInput(BaseModel): question: str = Field(min_length=2); reason: Optional[str] = None
class PlaybookCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150); domain: str = Field(min_length=2, max_length=100)
    typical_requirements: list[str] = []; recommended_features: list[str] = []; common_integrations: list[str] = []; security_checklist: list[str] = []; deployment_checklist: list[str] = []; questions: list[PlaybookQuestionInput] = []
class PlaybookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID; name: str; domain: str; typical_requirements: list[str]; recommended_features: list[str]; common_integrations: list[str]; security_checklist: list[str]; deployment_checklist: list[str]; created_at: datetime
