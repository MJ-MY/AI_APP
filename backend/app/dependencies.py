from __future__ import annotations

# Depends / HTTPException / status：用于定义依赖注入和 HTTP 错误响应。
from fastapi import Depends, HTTPException, status
# HTTPBearer：用于从 Authorization 请求头中提取 Bearer Token。
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
# Session：数据库会话类型。
from sqlalchemy.orm import Session

# JWT 解码工具。
from .auth import decode_access_token
# 提供数据库 Session。
from .db import get_db
# User ORM 模型。
from .models import User

# bearer_scheme：统一读取 Authorization: Bearer xxx
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录用户。

    流程：
    1. 从请求头中读取 Bearer Token
    2. 解析 JWT 拿到用户 id
    3. 从数据库查询对应用户
    4. 返回当前用户对象，供受保护接口复用
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user