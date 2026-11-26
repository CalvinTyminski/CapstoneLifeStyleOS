
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Goal(Base):
    __tablename__ = "goals"

    __table_args__ = (
        CheckConstraint(
            "reward_amount > 0",
            name="ck_goal_positive_reward",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    start_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    end_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )

    reward_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class GoalCompletion(Base):
    __tablename__ = "goal_completions"

    __table_args__ = (
        UniqueConstraint(
            "goal_id",
            name="uq_goal_completion_once",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    goal_id: Mapped[int] = mapped_column(
        ForeignKey("goals.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    transaction_id: Mapped[UUID] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
