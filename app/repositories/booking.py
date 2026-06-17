from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking
from app.domain.enums import BookingStatus
from app.schemas import BookingCreateRequest


class BookingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        return await self.db.get(Booking, booking_id)

    async def get_by_id_for_update(self, booking_id: UUID) -> Booking | None:
        stmt = select(Booking).where(Booking.id == booking_id).with_for_update()
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, booking: BookingCreateRequest) -> Booking:
        booking = Booking(**booking.model_dump())
        self.db.add(booking)
        await self.db.flush()
        await self.db.refresh(booking)

        return booking

    async def list_bookings(
        self,
        *,
        status: BookingStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Booking], int]:
        filters = []
        if status is not None:
            filters.append(Booking.status == status)

        count_stmt = select(func.count()).select_from(Booking).where(*filters)
        total = int(await self.db.scalar(count_stmt) or 0)

        stmt = (
            select(Booking)
            .where(*filters)
            .order_by(Booking.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def update_status(self, booking: Booking, status: BookingStatus) -> Booking:
        booking.status = status
        await self.db.flush()
        await self.db.refresh(booking)
        return booking
