from uuid import UUID

from app.db.session import session_scope
from app.services.booking import BookingService
from app.worker.broker import broker


@broker.task
async def confirm_booking_task(booking_id: str) -> None:
    async with session_scope() as session:
        await BookingService(session).confirm(UUID(booking_id))
