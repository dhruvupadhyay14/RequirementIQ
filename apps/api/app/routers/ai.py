from fastapi import APIRouter, Depends, Path, status
from uuid import UUID
from app.database import get_db
from app.dependencies.auth import get_current_company_id
from app.repositories.ai_repository import AIRepository
from app.services.ai_service import AIService
from app.schemas.ai import AIAnalysisResponse, AIQuestionResponse, AIQuestionUpdate, RequirementResponse, RequirementUpdate

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze/{meeting_id}", response_model=AIAnalysisResponse, status_code=status.HTTP_200_OK)
def analyze_meeting(
    meeting_id: UUID = Path(...),
    transcript: str | None = None,
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
):
    repository = AIRepository(db)
    service = AIService(repository, db)
    return service.analyze_meeting(meeting_id, company_id, transcript)


@router.get("/questions/{meeting_id}", response_model=list[AIQuestionResponse])
def list_questions(
    meeting_id: UUID = Path(...),
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
):
    repository = AIRepository(db)
    service = AIService(repository, db)
    return service.list_questions(meeting_id, company_id)


@router.get("/requirements/{meeting_id}", response_model=list[RequirementResponse])
def list_requirements(
    meeting_id: UUID = Path(...),
    db=Depends(get_db),
    company_id: UUID = Depends(get_current_company_id),
):
    repository = AIRepository(db)
    service = AIService(repository, db)
    return service.list_requirements(meeting_id, company_id)


@router.patch("/requirements/{requirement_id}", response_model=RequirementResponse)
def update_requirement(requirement_id: UUID, requirement_in: RequirementUpdate, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id)):
    return AIService(AIRepository(db), db).update_requirement(requirement_id, company_id, requirement_in.model_dump(exclude_unset=True))


@router.patch("/questions/{question_id}", response_model=AIQuestionResponse)
def update_question(question_id: UUID, question_in: AIQuestionUpdate, db=Depends(get_db), company_id: UUID = Depends(get_current_company_id)):
    return AIService(AIRepository(db), db).update_question(question_id, company_id, question_in.status)
