from datetime import datetime
from uuid import UUID, uuid7

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.enums import BookingStatus


class Booking(Base):
    __tablename__ = "Bookings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    service_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(
            BookingStatus,
            name="bookingstatus",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=BookingStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
