from __future__ import annotations

# contextmanager：把普通函数包装成 with 可用的上下文管理器。
from contextlib import contextmanager
# Iterator：用于标注生成器返回类型。
from typing import Iterator

# create_engine：创建 SQLAlchemy 数据库引擎。
from sqlalchemy import create_engine
# Session / declarative_base / sessionmaker：用于 ORM 会话和模型基类。
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# 读取数据库连接配置。
from .config import get_settings


settings = get_settings()

# engine：整个应用共享的数据库连接引擎。
engine = create_engine(
    settings.database_url,
    future=True,
)

# SessionLocal：每次请求创建一个独立数据库会话。
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

# Base：所有 ORM 模型的基类。
Base = declarative_base()


def get_db() -> Iterator[Session]:
    """
    FastAPI 依赖函数。

    为每个请求提供一个数据库 Session，请求结束后自动关闭。
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Iterator[Session]:
    """
    通用数据库上下文。

    适合在脚本或后台任务中使用 with db_session() 的方式管理事务。
    """

    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

