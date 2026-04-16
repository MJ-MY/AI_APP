from __future__ import annotations

import os
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv


# 读取环境变量文件（本地开发用）
# - 你可以在 backend/.env.local 里放 MINIMAX_API_KEY
# - 也可以放在 backend/.env
# - 也兼容你当前的文件放置：backend/app/.env.local
# - 环境变量优先级：系统环境变量 > .env.local/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env.local"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.local"))

app = FastAPI(title="ai-app-backend", version="0.1.0")


@app.get("/health")
async def health():
    return JSONResponse(
        {
            "ok": True,
            "service": "backend",
            "minimax_key_configured": bool(os.environ.get("MINIMAX_API_KEY")),
        }
    )


@app.post("/v1/chat/stream")
async def chat_stream(request: Request):
    """
    Minimal SSE endpoint.

    - For now: streams a placeholder message.
    - Next step: replace `iterator()` with a real MiniMax streaming call.
    """

    _ = await request.body()

    async def iterator() -> AsyncIterator[bytes]:
        yield b"event: message\ndata: {\"type\":\"delta\",\"content\":\"Backend is running. Next: connect MiniMax.\"}\n\n"
        yield b"event: message\ndata: {\"type\":\"done\"}\n\n"

    return StreamingResponse(iterator(), media_type="text/event-stream")


# --- Optional: MiniMax streaming (hook point) ---
# When you're ready, you can implement a function like below and use it in /v1/chat/stream.
#
# MINIMAX_BASE = "https://api.minimax.io"
# MINIMAX_PATH = "/v1/text/chatcompletion_v2"
#
# async def minimax_stream(payload: dict) -> AsyncIterator[bytes]:
#     api_key = os.environ["MINIMAX_API_KEY"]
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json",
#         "Accept": "text/event-stream",
#     }
#     payload = {**payload, "stream": True}
#     async with httpx.AsyncClient(timeout=None) as client:
#         async with client.stream(
#             "POST",
#             f"{MINIMAX_BASE}{MINIMAX_PATH}",
#             headers=headers,
#             json=payload,
#         ) as r:
#             r.raise_for_status()
#             async for chunk in r.aiter_raw():
#                 yield chunk

