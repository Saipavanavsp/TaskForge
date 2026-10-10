import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger("taskforge.db")

# Decide engine URL
engine_url = settings.DATABASE_URL
connect_args = {}

if "sqlite" in engine_url:
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    engine_url,
    echo=False,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    try:
        from sqlalchemy import text
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return False
