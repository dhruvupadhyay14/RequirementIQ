from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    AI_PROVIDER: str = "fallback"
    AI_REQUEST_TIMEOUT_SECONDS: int = 30
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None
    CHROMA_HOST: str | None = None
    CORS_ORIGINS: List[str] = ["*"]
    PYTHON_ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
