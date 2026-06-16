from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking
from app.domain import BookingStatus
from app.repositories import BookingRepository
from app.schemas import BookingCreateRequest, BookingListResponse, BookingResponse


class BookingService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = BookingRepository(session)

    async def create(self, payload: BookingCreateRequest) -> Booking:
        return await self._repository.create(payload)

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
