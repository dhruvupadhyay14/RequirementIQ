from pydantic import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    OPENAI_API_KEY: str | None = None
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    CHROMA_HOST: str | None = None
    CORS_ORIGINS: List[str] = ["*"]
    PYTHON_ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
