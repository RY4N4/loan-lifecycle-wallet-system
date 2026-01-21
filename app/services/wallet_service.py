from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.wallet import Wallet
from app.models.user import User
from decimal import Decimal
from fastapi import HTTPException, status


class WalletService:
    """
    Wallet Service - Manages user wallet balances
    
    Key Principles:
    1. Balance can never be negative (enforced by DB constraint)
    2. All balance changes must be transactional
    3. Balance changes must create transaction ledger entries
    """

    @staticmethod
    def create_wallet(db: Session, user_id: int) -> Wallet:
        """
        Create a wallet for a new user with zero balance
        """
        wallet = Wallet(user_id=user_id, balance=Decimal("0.00"))
        db.add(wallet)
        db.flush()
        return wallet

    @staticmethod
    def get_wallet(db: Session, user_id: int) -> Wallet:
        """Get user's wallet"""
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
        return wallet

    @staticmethod
    def credit_wallet(
        db: Session,
        user_id: int,
        amount: Decimal
    ) -> Wallet:
        """
        Credit amount to wallet (used during loan disbursement)
        
        This method MUST be called within a transaction that also
        creates a ledger entry.
        """
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Credit amount must be positive"
            )

        wallet = WalletService.get_wallet(db, user_id)
        wallet.balance += amount
        db.flush()
        return wallet

    @staticmethod
    def debit_wallet(
        db: Session,
        user_id: int,
        amount: Decimal
    ) -> Wallet:
        """
        Debit amount from wallet (used during repayment)
        
        This method MUST be called within a transaction that also
        creates a ledger entry.
        
        Raises:
            HTTPException: If insufficient balance
        """
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debit amount must be positive"
            )

        wallet = WalletService.get_wallet(db, user_id)
        
        if wallet.balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: {wallet.balance}, Required: {amount}"
            )

        wallet.balance -= amount
        
        # DB constraint will raise error if balance goes negative
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction would result in negative balance"
            )
        
        return wallet

    @staticmethod
    def check_wallet_activity(db: Session, user_id: int) -> bool:
        """
        Mock rule: Check if user has had wallet activity
        
        In production, this would check:
        - Transaction count
        - Total volume
        - Account age
        """
        wallet = WalletService.get_wallet(db, user_id)
        # Simple mock: wallet exists = eligible
        return wallet is not None
