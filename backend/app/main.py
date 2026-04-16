from __future__ import annotations

import os
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv

from .config import get_settings
from .schemas import ChatDelta, ChatRequest, HealthResponse, sse_message


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env.local"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.local"))

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        ok=True,
        service="backend",
        minimax_key_configured=bool(settings.minimax_api_key),
    )


@app.post("/v1/chat/stream")
async def chat_stream(request: Request) -> StreamingResponse:
    """
    SSE endpoint with a unified ChatDelta schema.

    - For now: echoes a placeholder delta and done event.
    - Next: replace `iterator()` with a real streaming call to your model provider.
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
        delta = ChatDelta(
            type="delta",
            content="Backend is running. Next: connect real model + conversations.",
            error=None,
        )
        yield sse_message("message", delta.model_dump_json())

        done = ChatDelta(type="done", content=None, error=None)
        yield sse_message("message", done.model_dump_json())

    return StreamingResponse(iterator(), media_type="text/event-stream")

