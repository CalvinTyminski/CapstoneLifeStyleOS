from datetime import date
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.goal import Goal, GoalCompletion
from app.models.wallet import Wallet
from app.models.ledger import LedgerEntry


GOAL_REWARDS = {
    "FITNESS": Decimal("50.00"),
    "NUTRITION": Decimal("30.00"),
    "HABIT": Decimal("20.00"),
}


def get_goal_reward(goal_type: str) -> Decimal:
    normalized_type = goal_type.upper()

    if normalized_type not in GOAL_REWARDS:
        raise ValueError("Unsupported goal type")

    return GOAL_REWARDS[normalized_type]


class GoalError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def complete_goal(
    db: Session,
    user_id: int,
    goal_id: int,
):
    try:
        goal = db.execute(
            select(Goal).where(
                Goal.id == goal_id,
                Goal.user_id == user_id,
            )
        ).scalar_one_or_none()

        if goal is None:
            raise GoalError("Goal not found", 404)

        # Lock the wallet to serialize reward transactions.
        wallet = db.execute(
            select(Wallet)
            .where(Wallet.user_id == user_id)
            .with_for_update()
        ).scalar_one_or_none()

        if wallet is None:
            raise GoalError("Wallet not found", 404)

        # Check after acquiring the wallet lock.
        existing = db.execute(
            select(GoalCompletion).where(
                GoalCompletion.goal_id == goal_id
            )
        ).scalar_one_or_none()

        if existing is not None:
            result = {
                "goal_id": goal_id,
                "transaction_id": existing.transaction_id,
                "reward_amount": goal.reward_amount,
                "balance": wallet.balance,
                "already_completed": True,
            }
            db.commit()
            return result

        today = date.today()

        if today < goal.start_date:
            raise GoalError("Goal has not started", 409)

        if goal.end_date is not None and today > goal.end_date:
            raise GoalError("Goal has expired", 409)

        transaction_id = uuid4()

        # Update wallet balance.
        wallet.balance += goal.reward_amount

        # Record wallet credit.
        entry = LedgerEntry(
            wallet_id=wallet.id,
            transaction_id=transaction_id,
            event_type="REWARD",
            amount=goal.reward_amount,
            idempotency_key=f"goal-completion:{goal.id}",
        )
        db.add(entry)

        # Record goal completion.
        completion = GoalCompletion(
            goal_id=goal.id,
            user_id=user_id,
            transaction_id=transaction_id,
        )
        db.add(completion)

        # Inserts must succeed before committing.
        db.flush()

        result = {
            "goal_id": goal.id,
            "transaction_id": transaction_id,
            "reward_amount": goal.reward_amount,
            "balance": wallet.balance,
            "already_completed": False,
        }

        db.commit()
        return result

    except Exception:
        db.rollback()
        raise

