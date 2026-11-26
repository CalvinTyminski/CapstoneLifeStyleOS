
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.store_item import StoreItem
from app.models.purchase import Purchase
from app.schemas.store import (
    StoreItemResponse,
    PurchaseRequest,
    PurchaseResponse,
    PurchaseHistoryItem,
)
from app.services.store_service import (
    StoreError,
    purchase_item,
)


router = APIRouter(
    prefix="/api/store",
    tags=["Store"],
)


@router.get(
    "/items",
    response_model=list[StoreItemResponse],
)
def list_store_items(
    db: Session = Depends(get_db),
):
    return db.execute(
        select(StoreItem)
        .where(StoreItem.is_active.is_(True))
        .order_by(StoreItem.id)
    ).scalars().all()


@router.post(
    "/purchases",
    response_model=PurchaseResponse,
)
def create_purchase(
    data: PurchaseRequest,
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            min_length=8,
            max_length=64,
        ),
    ],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return purchase_item(
            db=db,
            user_id=current_user.id,
            item_id=data.item_id,
            idempotency_key=idempotency_key,
        )
    except StoreError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        )


@router.get(
    "/purchases",
    response_model=list[PurchaseHistoryItem],
)
def list_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = db.execute(
        select(Purchase, StoreItem.name)
        .join(StoreItem, Purchase.item_id == StoreItem.id)
        .where(Purchase.user_id == current_user.id)
        .order_by(
            Purchase.purchased_at.desc(),
            Purchase.id.desc(),
        )
        .limit(100)
    ).all()

    return [
        PurchaseHistoryItem(
            purchase_id=purchase.id,
            transaction_id=purchase.transaction_id,
            item_id=purchase.item_id,
            item_name=item_name,
            amount_paid=purchase.amount_paid,
            purchased_at=purchase.purchased_at.isoformat(),
        )
        for purchase, item_name in results
    ]
