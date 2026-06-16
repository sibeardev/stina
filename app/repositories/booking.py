from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking
from app.schemas import BookingCreateRequest


class BookingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        return await self.db.get(Booking, booking_id)

    async def create(self, booking: BookingCreateRequest) -> Booking:
        booking = Booking(**booking.model_dump())
        self.db.add(booking)
        await self.db.flush()
        await self.db.refresh(booking)

        return booking
