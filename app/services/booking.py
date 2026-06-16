from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking
from app.domain.enums import BookingStatus
from app.repositories import BookingRepository
from app.schemas import BookingCreateRequest, BookingListResponse, BookingResponse


class BookingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = BookingRepository(session)

    async def create(self, payload: BookingCreateRequest) -> Booking:
        return await self._repository.create(payload)

    async def get_booking_status(self, booking_id: UUID) -> BookingStatus | None:
        booking = await self._repository.get_by_id(booking_id)
        if booking:
            return booking.status

    async def cancel_booking(self, booking_id: UUID) -> Booking:
        booking = await self._repository.get_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        if booking.status != BookingStatus.PENDING:
            raise ValueError("Booking is not pending")
        return await self._repository.cancel(booking)

    async def list_bookings(
        self,
        *,
        status: BookingStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> BookingListResponse:
        bookings, total = await self._repository.list_bookings(
            status=status,
            offset=offset,
            limit=limit,
        )
        return BookingListResponse(
            items=[BookingResponse.model_validate(booking) for booking in bookings],
            total=total,
            offset=offset,
            limit=limit,
        )
