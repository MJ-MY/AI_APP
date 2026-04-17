from __future__ import annotations

# os：用于定位并加载本地环境变量文件。
import os
# AsyncIterator：用于标注流式响应生成器的返回类型。
from typing import AsyncIterator

# asynccontextmanager：用于定义 FastAPI 启动/关闭生命周期。
from contextlib import asynccontextmanager

# FastAPI / Depends / HTTPException / Request / status：用于定义接口、依赖和错误处理。
from fastapi import Depends, FastAPI, HTTPException, Request, status
# CORSMiddleware：用于配置跨域访问规则。
from fastapi.middleware.cors import CORSMiddleware
# StreamingResponse：用于返回 SSE 流；JSONResponse 可按需返回普通 JSON。
from fastapi.responses import StreamingResponse
# select：用于编写 SQLAlchemy 查询。
from sqlalchemy import select
# OperationalError：数据库连接失败等运行时错误。
from sqlalchemy.exc import OperationalError
# Session：数据库会话类型。
from sqlalchemy.orm import Session
# load_dotenv：用于加载 .env / .env.local 环境变量文件。
from dotenv import load_dotenv

# 项目配置。
from .config import get_settings
# JWT 和密码工具。
from .auth import create_access_token, hash_password, verify_password
# 数据库基类、引擎和依赖。
from .db import Base, engine, get_db
# 当前登录用户依赖。
from .dependencies import get_current_user
# 导入模型，确保 Base.metadata.create_all 时能注册数据表。
from . import models
# User ORM 模型。
from .models import User
# 请求与响应模型。
from .schemas import (
    AuthTokenResponse,
    ChatDelta,
    ChatRequest,
    HealthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
    sse_message,
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env.local"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.local"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期钩子。

    启动时自动创建当前已声明的数据库表，便于本地开发快速跑通。
    """

    # 注意：如果本机 Postgres 没启动/连不上（例如 5432 端口未监听），这里会抛异常导致服务起不来。
    # 为了让你能先跑通服务与健康检查，我们在开发阶段选择“连不上就跳过建表”。
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:  # noqa: BLE001
        pass
    yield


settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    健康检查接口。

    用于验证服务是否启动，以及模型密钥是否已配置。
    """

    return HealthResponse(
        ok=True,
        service="backend",
        minimax_key_configured=bool(settings.minimax_api_key),
    )


@app.post("/v1/auth/register", response_model=AuthTokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    """
    用户注册接口。

    校验邮箱是否已存在，创建用户后立即返回访问令牌。
    """

    try:
        existing = db.scalar(select(User).where(User.email == payload.email))
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            display_name=payload.display_name,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except OperationalError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "数据库连接失败：请确认 Postgres 已启动，并且 DATABASE_URL 配置正确。"
                " 你可以运行项目根目录的 docker-compose.yml：docker compose up -d postgres"
            ),
        ) from exc

    token = create_access_token(user.id)
    return AuthTokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@app.post("/v1/auth/login", response_model=AuthTokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthTokenResponse:
    """
    用户登录接口。

    使用邮箱和密码校验身份，成功后签发新的访问令牌。
    """

    try:
        user = db.scalar(select(User).where(User.email == payload.email))
    except OperationalError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "数据库连接失败：请确认 Postgres 已启动，并且 DATABASE_URL 配置正确。"
                " 你可以运行项目根目录的 docker-compose.yml：docker compose up -d postgres"
            ),
        ) from exc

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id)
    return AuthTokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@app.get("/v1/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    获取当前登录用户信息。

    该接口依赖 Bearer Token，用于前端判断当前登录状态。
    """

    return UserResponse.model_validate(current_user)


@app.post("/v1/chat/stream")
async def chat_stream(request: Request) -> StreamingResponse:
    """
    流式聊天接口。

    当前先返回占位流式响应，后续会在这里接入真实模型与会话持久化。
    """

    try:
        body = await request.json()
        _ = ChatRequest.model_validate(body)
    except Exception as exc:  # noqa: BLE001
        async def error_iterator() -> AsyncIterator[bytes]:
            payload = ChatDelta(type="error", error=str(exc), content=None)
            yield sse_message("message", payload.model_dump_json())

        return StreamingResponse(error_iterator(), media_type="text/event-stream")

    async def iterator() -> AsyncIterator[bytes]:
        """
        SSE 内容生成器。

        按顺序输出一条 delta 消息和一条 done 消息。
        """

        delta = ChatDelta(
            type="delta",
            content="Backend is running. Next: connect real model + conversations.",
            error=None,
        )
        yield sse_message("message", delta.model_dump_json())

        done = ChatDelta(type="done", content=None, error=None)
        yield sse_message("message", done.model_dump_json())

    return StreamingResponse(iterator(), media_type="text/event-stream")

