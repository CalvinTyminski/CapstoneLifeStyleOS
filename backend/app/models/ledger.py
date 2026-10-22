from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    __table_args__ = (
        CheckConstraint(
            "amount <> 0",
            name="ck_ledger_nonzero_amount",
        ),
        CheckConstraint(
            "event_type IN ('DEPOSIT', 'REWARD', 'PURCHASE')",
            name="ck_ledger_event_type",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id"),
        nullable=False,
    )

    transaction_id: Mapped[UUID] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
        default=uuid4,
    )

    event_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )