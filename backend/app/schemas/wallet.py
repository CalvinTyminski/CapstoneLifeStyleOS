
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class MockDepositRequest(BaseModel):
    amount: Decimal = Field(
        gt=Decimal("0"),
        le=Decimal("1000.00"),
        max_digits=6,
        decimal_places=2,
        allow_inf_nan=False,
    )


class WalletResponse(BaseModel):
    balance: Decimal


class DepositResponse(BaseModel):
    transaction_id: UUID
    amount: Decimal
    balance: Decimal
    already_processed: bool


class TransactionResponse(BaseModel):
    transaction_id: UUID
    event_type: str
    amount: Decimal
    created_at: str
