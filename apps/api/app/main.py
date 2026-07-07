from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config.settings import settings
from app.database import Base, engine
from app.models.company import Company
from app.models.workspace import Workspace
from app.models.user import User
from app.models.project import Project
from app.routers.auth import router as auth_router
from app.routers.project import router as project_router

app = FastAPI(title="RequirementIQ API", version="0.1.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("requirementiq")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(project_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
