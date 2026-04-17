from __future__ import annotations

# datetime / timedelta / timezone：用于生成带过期时间的 JWT。
from datetime import datetime, timedelta, timezone
# Any：用于声明 JWT payload 的通用字典类型。
from typing import Any

# jose.jwt：用于编码与解码 JWT。
from jose import jwt
# bcrypt：用于密码哈希与校验（避免 passlib 与 bcrypt 5.x 的兼容性问题）。
import bcrypt

# 读取项目配置，例如 JWT 密钥、算法和过期时间。
from .config import get_settings

# 加载全局配置，供 token 编解码复用。
settings = get_settings()


def hash_password(password: str) -> str:
    """
    对用户明文密码做哈希，数据库中只保存哈希后的结果。
    """

    # bcrypt 只支持最多 72 字节；这里做截断，避免极端长密码触发异常。
    secret = password.encode("utf-8")[:72]
    hashed = bcrypt.hashpw(secret, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    校验用户输入的明文密码是否与数据库中的哈希值匹配。
    """

    secret = password.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(secret, password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str) -> str:
    """
    生成访问令牌。

    subject 一般放用户 id，后续通过解析 token 找回当前用户。
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expires_minutes
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    解析访问令牌，返回解码后的 payload。
    """

    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])