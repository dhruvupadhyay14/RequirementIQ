from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.config.settings import settings
from app.models.base import Base


engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
