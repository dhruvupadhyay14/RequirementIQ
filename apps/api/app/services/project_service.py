from uuid import UUID
from fastapi import HTTPException, status
from app.models.project import ProjectPriority, ProjectStatus
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse, ProjectUpdate
from datetime import datetime


class ProjectService:
    def __init__(self, db):
        self.repository = ProjectRepository(db)
        self.db = db

    def create_project(self, company_id: UUID, user_id: UUID, payload: ProjectCreate) -> ProjectResponse:
        if self.repository.get_project_by_title(company_id, payload.title):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project title already exists for this company")

        record = self.repository.create_project(
            {
                "company_id": company_id,
                "title": payload.title,
                "description": payload.description,
                "industry": payload.industry,
                "client_name": payload.client_name,
                "client_email": payload.client_email,
                "client_company": payload.client_company,
                "budget": payload.budget,
                "currency": payload.currency,
                "priority": payload.priority,
                "status": payload.status,
                "expected_start_date": payload.expected_start_date,
                "expected_end_date": payload.expected_end_date,
                "created_by": user_id,
                "updated_by": user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        self.db.commit()
        return ProjectResponse.model_validate(record)

    def list_projects(self, company_id: UUID, limit: int = 10, offset: int = 0, status: str | None = None, priority: str | None = None, industry: str | None = None, search: str | None = None, sort_by: str | None = None, sort_order: str = "asc") -> ProjectListResponse:
        projects, total = self.repository.list_projects(company_id, limit, offset, status, priority, industry, search, sort_by, sort_order)
        return ProjectListResponse(projects=projects, total=total)

    def get_project(self, company_id: UUID, project_id: UUID) -> ProjectResponse:
        project = self.repository.get_project_by_id(project_id)
        if not project or project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return ProjectResponse.model_validate(project)

    def update_project(self, company_id: UUID, user_id: UUID, project_id: UUID, payload: ProjectUpdate) -> ProjectResponse:
        project = self.repository.get_project_by_id(project_id)
        if not project or project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if payload.title and payload.title != project.title:
            existing = self.repository.get_project_by_title(company_id, payload.title)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project title already exists for this company")

        updates = payload.model_dump(exclude_none=True)
        updates["updated_by"] = user_id
        updates["updated_at"] = datetime.utcnow()
        updated = self.repository.update_project(project, updates)
        self.db.commit()
        return ProjectResponse.model_validate(updated)

    def delete_project(self, company_id: UUID, project_id: UUID) -> dict[str, str]:
        project = self.repository.get_project_by_id(project_id)
        if not project or project.company_id != company_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        self.repository.soft_delete_project(project)
        self.db.commit()
        return {"message": "Project deleted"}
