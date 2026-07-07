from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.models.project import ProjectPriority, ProjectStatus


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    industry: Optional[str] = None
    client_name: str = Field(..., min_length=1)
    client_email: Optional[EmailStr] = None
    client_company: Optional[str] = None
    budget: Optional[float] = None
    currency: Optional[str] = "USD"
    priority: ProjectPriority = ProjectPriority.MEDIUM
    status: ProjectStatus = ProjectStatus.DISCOVERY
    expected_start_date: Optional[datetime] = None
    expected_end_date: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    title: Optional[str] = None
    client_name: Optional[str] = None
    priority: Optional[ProjectPriority] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    title: str
    description: Optional[str]
    industry: Optional[str]
    client_name: str
    client_email: Optional[str]
    client_company: Optional[str]
    budget: Optional[float]
    currency: str
    priority: ProjectPriority
    status: ProjectStatus
    expected_start_date: Optional[datetime]
    expected_end_date: Optional[datetime]
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
