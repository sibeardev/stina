from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_scope() as session:
        yield session


engine = create_async_engine(str(settings.database_url), echo=settings.debug)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
