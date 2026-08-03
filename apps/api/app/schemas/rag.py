from uuid import UUID
from pydantic import BaseModel, Field
class SearchRequest(BaseModel): project_id: UUID; query: str = Field(min_length=2, max_length=2000); limit: int = Field(default=5, ge=1, le=20)
class SearchResult(BaseModel): text: str; metadata: dict; score: float
class IndexResponse(BaseModel): indexed_chunks: int
