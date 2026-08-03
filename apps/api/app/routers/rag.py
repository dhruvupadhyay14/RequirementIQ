from uuid import UUID
from fastapi import APIRouter, Depends
from app.database import get_db
from app.dependencies.auth import get_current_company_id
from app.rag.knowledge_service import KnowledgeService
from app.schemas.rag import IndexResponse, SearchRequest, SearchResult
router = APIRouter(prefix="/rag", tags=["knowledge-base"])
@router.post("/index/{meeting_id}", response_model=IndexResponse)
def index(meeting_id: UUID, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id)): return {"indexed_chunks": KnowledgeService(db).index_meeting(meeting_id, company_id)}
@router.post("/search", response_model=list[SearchResult])
def search(body: SearchRequest, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id)): return KnowledgeService(db).search(body.project_id, company_id, body.query, body.limit)
@router.get("/project-memory/{project_id}")
def memory(project_id: UUID, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id)): return KnowledgeService(db).project_memory(project_id, company_id)
