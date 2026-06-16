from fastapi import APIRouter, Query, status

from app.api.deps import BookingServiceDep
from app.domain import BookingStatus
from app.schemas import BookingCreateRequest, BookingListResponse, BookingResponse

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingResponse,
)
async def create_booking(
    payload: BookingCreateRequest,
    service: BookingServiceDep,
) -> BookingResponse:
    booking = await service.create(payload)
    return BookingResponse.model_validate(booking)


@router.get("", response_model=BookingListResponse)
async def list_bookings(
    service: BookingServiceDep,
    status: BookingStatus | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> BookingListResponse:
    return await service.list_bookings(status=status, offset=offset, limit=limit)
