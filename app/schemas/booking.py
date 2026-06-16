from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import BookingStatus


class BookingCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=255)
    datetime: datetime
    service_type: str = Field(min_length=1, max_length=255)

    @field_validator("datetime")
    @classmethod
    def validate_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            msg = "datetime must be timezone-aware"
            raise ValueError(msg)
        if value <= datetime.now(UTC):
            msg = "datetime must be in the future"
            raise ValueError(msg)
        return value


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    datetime: datetime
    service_type: str
    status: BookingStatus
    created_at: datetime


class BookingListResponse(BaseModel):
    items: list[BookingResponse]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
