from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    ok: bool
    service: str
    minimax_key_configured: bool


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    kb_id: Optional[str] = None
    mode: Literal["plain", "rag"] = "plain"
    messages: list[ChatMessage]


class ChatDelta(BaseModel):
    type: Literal["delta", "done", "error"]
    content: str | None = None
    error: str | None = None


def sse_message(event: str, data: str) -> bytes:
    """
    Build a minimal SSE message.
    """

    return f"event: {event}\ndata: {data}\n\n".encode("utf-8")

