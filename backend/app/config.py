import os
from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "ai-app-backend"
    env: str = os.getenv("APP_ENV", "local")
    debug: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

    # Database (for later phases: conversations / kb / tables)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://ai_app:ai_app@localhost:5432/ai_app",
    )

    # Auth (to be used when implementing auth-multiuser)
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60 * 24

    # AI provider (MiniMax etc.)
    minimax_api_key: str | None = os.getenv("MINIMAX_API_KEY")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

