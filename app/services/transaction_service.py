from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionType, TransactionSource
from decimal import Decimal
from typing import List


class TransactionService:
    """
    IMMUTABLE LEDGER SERVICE
    
    This is the source of truth for all financial operations.
    Every money movement MUST create a transaction entry.
    
    Key Principles:
    1. Append-only: No updates or deletes
    2. Complete audit trail
    3. Reconciliation ready
    """

    @staticmethod
    def create_transaction(
        db: Session,
        user_id: int,
        amount: Decimal,
        transaction_type: TransactionType,
        source: TransactionSource,
        reference_id: str,
        description: str = ""
    ) -> Transaction:
        """
        Create an immutable transaction record.
        
        This method is called by other services (loan, repayment)
        to record every money movement in the system.
        """
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=transaction_type,
            source=source,
            reference_id=reference_id,
            description=description
        )
        db.add(transaction)
        db.flush()  # Get the ID but don't commit yet
        return transaction

    @staticmethod
    def get_user_transactions(
        db: Session,
        user_id: int,
        limit: int = 100
    ) -> List[Transaction]:
        """Get transaction history for a user"""
        return (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_transaction_by_reference(
        db: Session,
        reference_id: str,
        source: TransactionSource
    ) -> Transaction:
        """Find transaction by reference (loan_id or repayment_id)"""
        return (
            db.query(Transaction)
            .filter(
                Transaction.reference_id == reference_id,
                Transaction.source == source
            )
            .first()
        )
