from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config.settings import settings
from app.database import engine
from app.models.company import Company
from app.models.workspace import Workspace
from app.models.user import User
from app.models.project import Project
from app.routers.auth import router as auth_router
from app.routers.project import router as project_router
from app.routers.meeting import router as meeting_router
from app.core.logging import configure_logging
from app.core.constants import VERSION

configure_logging()

app = FastAPI(title="RequirementIQ API", version=VERSION)

logging.getLogger("requirementiq")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(meeting_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
