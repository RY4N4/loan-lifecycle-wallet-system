from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.wallet import WalletResponse
from app.schemas.transaction import TransactionResponse
from app.services.wallet_service import WalletService
from app.services.transaction_service import TransactionService
from app.auth.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/api/wallet", tags=["Wallet"])


@router.get("/balance", response_model=WalletResponse)
def get_wallet_balance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current wallet balance
    """
    wallet = WalletService.get_wallet(db, current_user.id)
    return WalletResponse.model_validate(wallet)


@router.get("/transactions", response_model=List[TransactionResponse])
def get_wallet_transactions(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get wallet transaction history
    
    Returns immutable ledger entries showing all money movements
    """
    transactions = TransactionService.get_user_transactions(
        db, current_user.id, limit
    )
    return [TransactionResponse.model_validate(t) for t in transactions]
