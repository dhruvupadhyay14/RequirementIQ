from datetime import datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

DocumentType = Literal["srs", "brd", "mom", "client_summary", "technical"]

class DocumentGenerateRequest(BaseModel): document_type: DocumentType
class DocumentUpdate(BaseModel):
    status: Optional[Literal["draft", "approved"]] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    content: Optional[str] = Field(default=None, min_length=1)
class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID; project_id: UUID; meeting_id: UUID; document_type: str; title: str; content: str; version: int; status: str; created_by: UUID; created_at: datetime; updated_at: datetime
