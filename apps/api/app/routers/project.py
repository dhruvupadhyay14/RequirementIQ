from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService
from app.validation.auth_validation import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
def create_project(payload: ProjectCreate, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    service = ProjectService(db)
    return service.create_project(current_user.company_id, current_user.id, payload)


@router.get("", response_model=dict)
def list_projects(
    request: Request,
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0,
    status: str | None = None,
    priority: str | None = None,
    industry: str | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
):
    current_user = get_current_user(request, db)
    service = ProjectService(db)
    return service.list_projects(current_user.company_id, limit, offset, status, priority, industry, search, sort_by, sort_order).model_dump()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    service = ProjectService(db)
    return service.get_project(current_user.company_id, project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: UUID, payload: ProjectUpdate, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    service = ProjectService(db)
    return service.update_project(current_user.company_id, current_user.id, project_id, payload)


@router.delete("/{project_id}")
def delete_project(project_id: UUID, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    service = ProjectService(db)
    return service.delete_project(current_user.company_id, project_id)
