from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
import os
from unittest.mock import AsyncMock, patch

os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.db import models as _models  # noqa: F401
from app.db.base import Base
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True)
def mock_confirm_booking_task() -> AsyncIterator[AsyncMock]:
    with patch(
        "app.worker.tasks.confirm_booking_task.kiq",
        new_callable=AsyncMock,
    ) as mock_kiq:
        yield mock_kiq


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as http_client:
        yield http_client

    app.dependency_overrides.clear()


@pytest.fixture
def future_datetime() -> datetime:
    return datetime.now(UTC) + timedelta(days=7)


@pytest.fixture
def booking_payload(future_datetime: datetime) -> dict[str, str]:
    return {
        "name": "Ivan",
        "datetime": future_datetime.isoformat(),
        "service_type": "consultation",
    }


@pytest.fixture
async def created_booking(client: AsyncClient, booking_payload: dict[str, str]) -> dict:
    response = await client.post("/bookings", json=booking_payload)
    assert response.status_code == 201
    return response.json()
