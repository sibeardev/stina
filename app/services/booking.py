from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking
from app.repositories import BookingRepository
from app.schemas import BookingCreateRequest


class BookingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = BookingRepository(session)

    async def create(self, payload: BookingCreateRequest) -> Booking:
        return await self._repository.create(payload)
