from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from app.models.project import Project
from app.models.user import User


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_project_by_id(self, project_id: UUID) -> Project | None:
        return self.db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()

    def get_project_by_title(self, company_id: UUID, title: str) -> Project | None:
        return self.db.query(Project).filter(Project.company_id == company_id, Project.title == title, Project.deleted_at.is_(None)).first()

    def list_projects(self, company_id: UUID, limit: int = 10, offset: int = 0, status: str | None = None, priority: str | None = None, industry: str | None = None, search: str | None = None, sort_by: str | None = None, sort_order: str = "asc") -> tuple[list[Project], int]:
        query = self.db.query(Project).filter(Project.company_id == company_id, Project.deleted_at.is_(None))

        if status:
            query = query.filter(Project.status == status)
        if priority:
            query = query.filter(Project.priority == priority)
        if industry:
            query = query.filter(Project.industry == industry)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Project.title.ilike(search_term)
                | Project.description.ilike(search_term)
                | Project.client_name.ilike(search_term)
                | Project.client_company.ilike(search_term)
            )

        total = query.count()

        if sort_by in {"title", "created_at", "updated_at", "status", "priority"}:
            order_column = getattr(Project, sort_by)
            query = query.order_by(order_column.desc() if sort_order == "desc" else order_column.asc())
        else:
            query = query.order_by(Project.created_at.desc())

        projects = query.offset(offset).limit(limit).all()
        return projects, total

    def create_project(self, project: dict[str, any]) -> Project:
        record = Project(**project)
        self.db.add(record)
        self.db.flush()
        return record

    def update_project(self, project: Project, updates: dict[str, any]) -> Project:
        for field, value in updates.items():
            setattr(project, field, value)
        self.db.add(project)
        self.db.flush()
        return project

    def soft_delete_project(self, project: Project) -> Project:
        project.deleted_at = func.now()
        self.db.add(project)
        self.db.flush()
        return project

    def get_company_user(self, user_id: UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
