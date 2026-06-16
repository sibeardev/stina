"""create bookings table

Revision ID: a002815a74c3
Revises:
Create Date: 2026-06-16 09:38:34.541066

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a002815a74c3"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

booking_status_enum = sa.Enum(
    "pending",
    "confirmed",
    "failed",
    "cancelled",
    name="bookingstatus",
)


def upgrade() -> None:
    op.create_table(
        "Bookings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("service_type", sa.String(length=255), nullable=False),
        sa.Column("status", booking_status_enum, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bookings_datetime"), "Bookings", ["datetime"], unique=False)
    op.create_index(op.f("ix_bookings_status"), "Bookings", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_bookings_status"), table_name="Bookings")
    op.drop_index(op.f("ix_bookings_datetime"), table_name="Bookings")
    op.drop_table("Bookings")
    booking_status_enum.drop(op.get_bind(), checkfirst=True)
