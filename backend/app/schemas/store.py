
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StoreItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    price: Decimal
    category: str


class PurchaseRequest(BaseModel):
    item_id: int = Field(gt=0)


class PurchaseResponse(BaseModel):
    purchase_id: int
    transaction_id: UUID
    item_id: int
    amount_paid: Decimal
    balance: Decimal
    already_processed: bool


class PurchaseHistoryItem(BaseModel):
    purchase_id: int
    transaction_id: UUID
    item_id: int
    item_name: str
    amount_paid: Decimal
    purchased_at: str
