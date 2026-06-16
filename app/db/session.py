from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


engine = create_async_engine(str(settings.database_url), echo=settings.debug)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
