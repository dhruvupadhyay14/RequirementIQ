from datetime import datetime, date
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.analytics.chart_service import ChartService
from app.analytics.metrics_service import MetricsService
from app.models.document import Document
from app.models.meeting import Meeting
from app.models.project import Project, ProjectStatus
from app.models.requirement import AIQuestion, Requirement
from app.models.user import User, UserRole
from app.models.workspace_ai import WorkspaceDocument


class AnalyticsService:
    def __init__(self, db: Session, user: User):
        self.db, self.user = db, user

    def _resolve_user_scope(self):
        if self.user.role in {UserRole.COMPANY_ADMIN, UserRole.SUPER_ADMIN}:
            return [
                item.id
                for item in self.db.query(User)
                .filter(User.company_id == self.user.company_id, User.workspace_id == self.user.workspace_id)
                .all()
            ]
        return [self.user.id]

    def _apply_date_filters(self, query, model, field_name, date_from=None, date_to=None):
        if date_from is not None:
            query = query.filter(getattr(model, field_name) >= self._normalize_datetime(date_from))
        if date_to is not None:
            query = query.filter(getattr(model, field_name) <= self._normalize_datetime(date_to))
        return query

    def _normalize_datetime(self, value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        return datetime.fromisoformat(str(value))

    def _match_status(self, value, target):
        if target is None:
            return True
        if isinstance(value, str):
            return value == target
        if hasattr(value, "value"):
            return str(value.value) == target or str(value) == target
        return str(value) == target

    def _projects(self, project_id=None, status=None, date_from=None, date_to=None, workspace_id=None, domain=None):
        query = self.db.query(Project).filter(Project.company_id == self.user.company_id, Project.deleted_at.is_(None))
        if project_id is not None:
            query = query.filter(Project.id == project_id)
        if status is not None:
            query = query.filter(Project.status == status)
        if workspace_id is not None:
            user_ids = [item.id for item in self.db.query(User).filter(User.workspace_id == workspace_id).all()]
            query = query.filter(Project.created_by.in_(user_ids)) if user_ids else query.filter(False)
        else:
            user_ids = self._resolve_user_scope()
            query = query.filter(Project.created_by.in_(user_ids))
        if domain is not None:
            query = query.filter(or_(Project.industry == domain, Project.title.ilike(f"%{domain}%")))
        query = self._apply_date_filters(query, Project, "created_at", date_from, date_to)
        return query.all()

    def _meetings(self, project_ids=None, meeting_id=None, status=None, date_from=None, date_to=None):
        query = self.db.query(Meeting).filter(Meeting.deleted_at.is_(None))
        if project_ids is not None:
            query = query.filter(Meeting.project_id.in_(project_ids)) if project_ids else query.filter(False)
        if meeting_id is not None:
            query = query.filter(Meeting.id == meeting_id)
        if status is not None:
            query = query.filter(Meeting.status == status)
        query = self._apply_date_filters(query, Meeting, "scheduled_at", date_from, date_to)
        return query.all()

    def _requirements(self, project_ids=None, meeting_ids=None, status=None, date_from=None, date_to=None):
        query = self.db.query(Requirement)
        if project_ids is not None:
            query = query.filter(Requirement.project_id.in_(project_ids)) if project_ids else query.filter(False)
        if meeting_ids:
            query = query.filter(Requirement.meeting_id.in_(meeting_ids))
        if status is not None:
            query = query.filter(Requirement.status == status)
        query = self._apply_date_filters(query, Requirement, "created_at", date_from, date_to)
        return query.all()

    def _documents(self, project_ids=None, meeting_ids=None, date_from=None, date_to=None):
        query = self.db.query(Document)
        if project_ids is not None:
            query = query.filter(Document.project_id.in_(project_ids)) if project_ids else query.filter(False)
        if meeting_ids:
            query = query.filter(Document.meeting_id.in_(meeting_ids))
        query = self._apply_date_filters(query, Document, "created_at", date_from, date_to)
        return query.all()

    def _questions(self, meeting_ids=None, status=None, date_from=None, date_to=None):
        query = self.db.query(AIQuestion)
        if meeting_ids is not None:
            query = query.filter(AIQuestion.meeting_id.in_(meeting_ids)) if meeting_ids else query.filter(False)
        if status is not None:
            query = query.filter(AIQuestion.status == status)
        query = self._apply_date_filters(query, AIQuestion, "created_at", date_from, date_to)
        return query.all()

    def data(self, **filters):
        projects = self._projects(**filters)
        project_ids = [item.id for item in projects]
        meetings = self._meetings(project_ids=project_ids, **{key: value for key, value in filters.items() if key in {"meeting_id", "status", "date_from", "date_to"}})
        meeting_ids = [item.id for item in meetings]
        requirements = self._requirements(project_ids=project_ids, meeting_ids=meeting_ids, **{key: value for key, value in filters.items() if key in {"status", "date_from", "date_to"}})
        documents = self._documents(project_ids=project_ids, meeting_ids=meeting_ids, **{key: value for key, value in filters.items() if key in {"date_from", "date_to"}})
        questions = self._questions(meeting_ids=meeting_ids, **{key: value for key, value in filters.items() if key in {"status", "date_from", "date_to"}})
        return projects, meetings, requirements, documents, questions

    def overview(self, **filters):
        projects, meetings, requirements, documents, questions = self.data(**filters)
        approved = sum(item.status == "approved" for item in requirements)
        rejected = sum(item.status == "rejected" for item in requirements)
        return {
            "total_projects": len(projects),
            "total_meetings": len(meetings),
            "total_requirements": len(requirements),
            "documents_generated": len(documents),
            "ai_suggestions_generated": len(questions),
            "ai_suggestions_accepted": approved + sum(item.status == "answered" for item in questions),
            "ai_suggestions_rejected": rejected + sum(item.status == "dismissed" for item in questions),
            "requirement_completion_score": MetricsService.completion(requirements),
            "active_projects": sum(item.status not in {ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED} for item in projects),
            "completed_projects": sum(item.status == ProjectStatus.COMPLETED for item in projects),
        }

    def projects(self, **filters):
        projects, meetings, requirements, documents, _ = self.data(**filters)
        return [
            {
                "id": str(project.id),
                "title": project.title,
                "status": project.status.value if hasattr(project.status, "value") else str(project.status),
                "meeting_count": sum(item.project_id == project.id for item in meetings),
                "requirement_count": sum(item.project_id == project.id for item in requirements),
                "missing_requirements": sum(item.project_id == project.id and item.status == "pending" for item in requirements),
                "documents": sum(item.project_id == project.id for item in documents),
                "completion_percentage": MetricsService.completion([item for item in requirements if item.project_id == project.id]),
                "last_meeting_date": max((item.scheduled_at for item in meetings if item.project_id == project.id), default=None),
            }
            for project in projects
        ]

    def meetings(self, **filters):
        _, meetings, requirements, documents, questions = self.data(**filters)
        return [
            {
                "id": str(meeting.id),
                "title": meeting.title,
                "duration_minutes": meeting.duration_minutes or 0,
                "participants": len(meeting.participants),
                "transcript_length": sum(len(record.transcript or "") for record in meeting.conference_records),
                "requirements_extracted": sum(item.meeting_id == meeting.id for item in requirements),
                "questions_suggested": sum(item.meeting_id == meeting.id for item in questions),
                "questions_accepted": sum(item.meeting_id == meeting.id and item.status == "answered" for item in questions),
                "questions_rejected": sum(item.meeting_id == meeting.id and item.status == "dismissed" for item in questions),
                "documents": sum(item.meeting_id == meeting.id for item in documents),
            }
            for meeting in meetings
        ]

    def ai(self, **filters):
        projects, meetings, requirements, _, questions = self.data(**filters)
        return {
            "requirement_categories": MetricsService.categories(requirements),
            "confidence_score_average": MetricsService.confidence_average(requirements),
            "suggestion_acceptance_rate": round(100 * sum(item.status == "answered" for item in questions) / len(questions)) if questions else 0,
            "top_missing_requirement_categories": MetricsService.categories([item for item in requirements if item.status == "pending"]),
            "charts": {
                "project_status": ChartService.status(projects),
                "meetings_per_month": ChartService.monthly(meetings, "scheduled_at"),
                "requirements_over_time": ChartService.monthly(requirements),
                "suggestion_acceptance_trend": ChartService.monthly([item for item in questions if item.status == "answered"]),
                "project_completion": [
                    {"name": item.title, "value": MetricsService.completion([req for req in requirements if req.project_id == item.id])}
                    for item in projects
                ],
            },
        }

    def activity(self, **filters):
        projects, meetings, _, documents, questions = self.data(**filters)
        uploads = self.db.query(WorkspaceDocument).filter(WorkspaceDocument.workspace_id == self.user.workspace_id).all()
        items = (
            [{"type": "project", "title": item.title, "at": item.created_at} for item in projects]
            + [{"type": "meeting", "title": item.title, "at": item.created_at} for item in meetings]
            + [{"type": "document", "title": item.title, "at": item.created_at} for item in documents]
            + [{"type": "suggestion", "title": item.question, "at": item.created_at} for item in questions]
            + [{"type": "knowledge", "title": item.file_name, "at": item.created_at} for item in uploads]
        )
        return sorted(items, key=lambda item: item["at"], reverse=True)[:20]
