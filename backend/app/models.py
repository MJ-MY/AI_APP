from __future__ import annotations

# uuid：用于生成用户主键 id。
import uuid
# datetime：用于声明创建时间字段的类型。
from datetime import datetime

# SQLAlchemy 字段类型与 SQL 函数。
from sqlalchemy import Boolean, DateTime, String, func
# Mapped / mapped_column：SQLAlchemy 2.0 的 ORM 字段声明方式。
from sqlalchemy.orm import Mapped, mapped_column

# Base：所有 ORM 模型都需要继承它，才能被 metadata 管理。
from .db import Base


class User(Base):
    """
    用户表。

    用于支持注册、登录以及后续的多用户数据隔离。
    """

    __tablename__ = "users"

    # 用户主键，使用 uuid 字符串，便于前后端传递。
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    # 登录邮箱，要求唯一。
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    # 存储密码哈希，不保存明文密码。
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    # 用户展示名称。
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 是否启用该账号。
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # 创建时间，默认由数据库写入当前时间。
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
