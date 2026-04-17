from __future__ import annotations

# Literal / Optional：用于约束字段的可选值和可空类型。
from typing import Literal, Optional

# BaseModel / EmailStr / Field：用于定义请求响应模型和字段校验规则。
from pydantic import BaseModel, EmailStr, Field


class HealthResponse(BaseModel):
    """健康检查接口响应。"""

    ok: bool
    service: str
    minimax_key_configured: bool


class ChatMessage(BaseModel):
    """单条聊天消息。"""

    role: Literal["user", "assistant", "system"] = "user"
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """聊天请求体。"""

    conversation_id: Optional[str] = None
    kb_id: Optional[str] = None
    mode: Literal["plain", "rag"] = "plain"
    messages: list[ChatMessage]


class ChatDelta(BaseModel):
    """流式聊天返回的单个事件负载。"""

    type: Literal["delta", "done", "error"]
    content: str | None = None
    error: str | None = None


def sse_message(event: str, data: str) -> bytes:
    """
    构造一条最小可用的 SSE 消息。
    """

    return f"event: {event}\ndata: {data}\n\n".encode("utf-8")


class RegisterRequest(BaseModel):
    """注册请求体。"""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    """登录请求体。"""

    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    """对外返回的用户信息。"""

    id: str
    email: EmailStr
    display_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class AuthTokenResponse(BaseModel):
    """登录或注册成功后返回的 token 和用户信息。"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse