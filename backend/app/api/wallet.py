
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
from app.models.wallet import Wallet
from app.models.ledger import LedgerEntry
from app.schemas.wallet import (
    MockDepositRequest,
    WalletResponse,
    DepositResponse,
    TransactionResponse,
)
from app.services.wallet_service import add_mock_deposit


router = APIRouter(
    prefix="/api/wallet",
    tags=["Wallet"],
)


@router.get("", response_model=WalletResponse)
def get_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = db.execute(
        select(Wallet).where(
            Wallet.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if wallet is None:
        raise HTTPException(404, "Wallet not found")

    return WalletResponse(balance=wallet.balance)


@router.post(
    "/mock-deposits",
    response_model=DepositResponse,
)
def create_mock_deposit(
    data: MockDepositRequest,
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
        return add_mock_deposit(
            db=db,
            user_id=current_user.id,
            amount=data.amount,
            idempotency_key=idempotency_key,
        )
    except ValueError as exc:
        message = str(exc)

        if message == "Wallet not found":
            raise HTTPException(404, message)

        raise HTTPException(409, message)


@router.get(
    "/transactions",
    response_model=list[TransactionResponse],
)
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wallet = db.execute(
        select(Wallet).where(
            Wallet.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if wallet is None:
        raise HTTPException(404, "Wallet not found")

    entries = db.execute(
        select(LedgerEntry)
        .where(LedgerEntry.wallet_id == wallet.id)
        .order_by(LedgerEntry.created_at.desc(), LedgerEntry.id.desc())
        .limit(100)
    ).scalars().all()

    return [
        TransactionResponse(
            transaction_id=entry.transaction_id,
            event_type=entry.event_type,
            amount=entry.amount,
            created_at=entry.created_at.isoformat(),
        )
        for entry in entries
    ]
