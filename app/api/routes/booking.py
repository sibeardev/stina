from fastapi import APIRouter, status

from app.api.deps import BookingServiceDep
from app.schemas import BookingCreateRequest, BookingResponse

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
