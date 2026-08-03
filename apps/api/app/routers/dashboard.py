from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.analytics.analytics_service import AnalyticsService
from app.analytics.report_service import ReportService
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["analytics"])


def service(db, user):
    return AnalyticsService(db, user)


def _filters(project: Optional[UUID] = None, meeting: Optional[UUID] = None, date_from: Optional[date] = None, date_to: Optional[date] = None, status: Optional[str] = None, workspace: Optional[UUID] = None, domain: Optional[str] = None):
    return {
        "project_id": project,
        "meeting_id": meeting,
        "date_from": date_from,
        "date_to": date_to,
        "status": status,
        "workspace_id": workspace,
        "domain": domain,
    }


@router.get("/overview")
def overview(
    db=Depends(get_db),
    user: User = Depends(get_current_user),
    project: Optional[UUID] = Query(None),
    meeting: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    workspace: Optional[UUID] = Query(None),
    domain: Optional[str] = Query(None),
):
    return service(db, user).overview(**_filters(project, meeting, date_from, date_to, status, workspace, domain))


@router.get("/projects")
def projects(
    db=Depends(get_db),
    user: User = Depends(get_current_user),
    project: Optional[UUID] = Query(None),
    meeting: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    workspace: Optional[UUID] = Query(None),
    domain: Optional[str] = Query(None),
):
    return service(db, user).projects(**_filters(project, meeting, date_from, date_to, status, workspace, domain))


@router.get("/meetings")
def meetings(
    db=Depends(get_db),
    user: User = Depends(get_current_user),
    project: Optional[UUID] = Query(None),
    meeting: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    workspace: Optional[UUID] = Query(None),
    domain: Optional[str] = Query(None),
):
    return service(db, user).meetings(**_filters(project, meeting, date_from, date_to, status, workspace, domain))


@router.get("/ai")
def ai(
    db=Depends(get_db),
    user: User = Depends(get_current_user),
    project: Optional[UUID] = Query(None),
    meeting: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    workspace: Optional[UUID] = Query(None),
    domain: Optional[str] = Query(None),
):
    return service(db, user).ai(**_filters(project, meeting, date_from, date_to, status, workspace, domain))


@router.get("/activity")
def activity(
    db=Depends(get_db),
    user: User = Depends(get_current_user),
    project: Optional[UUID] = Query(None),
    meeting: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    workspace: Optional[UUID] = Query(None),
    domain: Optional[str] = Query(None),
):
    return service(db, user).activity(**_filters(project, meeting, date_from, date_to, status, workspace, domain))


@router.get("/export")
def export(
    format: str = Query("csv"),
    db=Depends(get_db),
    user: User = Depends(get_current_user),
    project: Optional[UUID] = Query(None),
    meeting: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    workspace: Optional[UUID] = Query(None),
    domain: Optional[str] = Query(None),
):
    try:
        data, media, suffix = ReportService().export(service(db, user).overview(**_filters(project, meeting, date_from, date_to, status, workspace, domain)), format)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Use csv, excel, or pdf") from exc
    return StreamingResponse(iter([data]), media_type=media, headers={"Content-Disposition": f'attachment; filename="analytics.{suffix}"'})
