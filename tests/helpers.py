from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking
from app.domain.enums import BookingStatus


async def set_booking_status(
    db_session: AsyncSession,
    booking_id: str,
    status: BookingStatus,
) -> None:
    booking = await db_session.get(Booking, UUID(booking_id))
    if booking is None:
        msg = f"booking {booking_id} not found"
        raise ValueError(msg)
    booking.status = status
    await db_session.flush()
