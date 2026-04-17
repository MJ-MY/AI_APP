# os：用于从环境变量中读取配置。
import os
# lru_cache：用于缓存配置对象，避免重复初始化。
from functools import lru_cache

# BaseModel：用来定义项目配置对象，统一管理环境变量。
from pydantic import BaseModel


class Settings(BaseModel):
    """
    项目运行配置。

    这里集中管理应用名、数据库地址、JWT、模型密钥等配置。
    """

    app_name: str = "ai-app-backend"
    env: str = os.getenv("APP_ENV", "local")
    debug: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

    # Database (for later phases: conversations / kb / tables)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://ai_app:ai_app@127.0.0.1:5432/ai_app",
    )

    # Auth (to be used when implementing auth-multiuser)
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60 * 24

    # AI provider (MiniMax etc.)
    minimax_api_key: str | None = os.getenv("MINIMAX_API_KEY")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    获取全局单例配置。

    使用缓存后，整个进程里只会初始化一次 Settings。
    """

    return Settings()

