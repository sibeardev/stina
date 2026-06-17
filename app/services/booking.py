from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking
from app.domain.enums import BookingStatus
from app.integrations.external import send_notification, should_fail_external_service
from app.repositories import BookingRepository
from app.schemas import BookingCreateRequest, BookingListResponse, BookingResponse


class BookingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = BookingRepository(session)

    async def create(self, payload: BookingCreateRequest) -> Booking:
        booking = await self._repository.create(payload)
        await self._session.commit()  # чтобы запись была готова к фоновой обработке
        return booking

    async def confirm(self, booking_id: UUID) -> None:
        booking = await self._repository.get_by_id_for_update(booking_id)
        if not booking or booking.status != BookingStatus.PENDING:
            return

        if should_fail_external_service():
            await self._repository.update_status(booking, BookingStatus.FAILED)
        else:
            await self._repository.update_status(booking, BookingStatus.CONFIRMED)
            send_notification(booking.name, str(booking.id))

    async def get_booking_status(self, booking_id: UUID) -> BookingStatus | None:
        booking = await self._repository.get_by_id(booking_id)
        if booking:
            return booking.status

    async def cancel(self, booking_id: UUID) -> Booking:
        booking = await self._repository.get_by_id_for_update(booking_id)
        if not booking:
            raise ValueError("Booking not found")
        if booking.status != BookingStatus.PENDING:
            raise ValueError("Booking is not pending")
        return await self._repository.update_status(booking, BookingStatus.CANCELLED)

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
