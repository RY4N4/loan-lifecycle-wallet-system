from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.repayment import Repayment, RepaymentType, RepaymentStatus
from app.models.loan import Loan, LoanStatus
from app.models.transaction import TransactionType, TransactionSource
from app.services.wallet_service import WalletService
from app.services.transaction_service import TransactionService
from app.services.loan_service import LoanService
from decimal import Decimal
from fastapi import HTTPException, status
from typing import Tuple


class RepaymentService:
    """
    Repayment Service - Handles loan repayments
    
    Key Features:
    1. Idempotency using client-provided keys
    2. Partial and full repayments
    3. Automatic loan closure when fully paid
    4. ACID transactions with wallet and ledger
    """

    @staticmethod
    def make_repayment(
        db: Session,
        user_id: int,
        loan_id: int,
        amount: Decimal,
        idempotency_key: str
    ) -> Tuple[Repayment, Loan]:
        """
        Process a loan repayment
        
        CRITICAL: ACID Transaction
        1. Check idempotency (prevent duplicate payments)
        2. Validate loan and amount
        3. Debit wallet
        4. Update loan outstanding
        5. Create repayment record
        6. Create transaction ledger entry
        7. Close loan if fully paid
        
        Args:
            idempotency_key: Client-generated unique key to prevent duplicate payments
        """
        
        # Step 1: Check idempotency - if already processed, return existing
        existing_repayment = (
            db.query(Repayment)
            .filter(Repayment.idempotency_key == idempotency_key)
            .first()
        )
        
        if existing_repayment:
            loan = LoanService.get_loan_by_id(db, existing_repayment.loan_id)
            return existing_repayment, loan

        # Step 2: Validate loan
        loan = LoanService.get_loan_by_id(db, loan_id)
        
        if loan.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to repay this loan"
            )

        if loan.status != LoanStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot repay loan in {loan.status} state"
            )

        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repayment amount must be positive"
            )

        if amount > loan.outstanding_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Repayment amount ({amount}) exceeds outstanding ({loan.outstanding_amount})"
            )

        try:
            # Step 3: Debit wallet
            WalletService.debit_wallet(db, user_id, amount)

            # Step 4: Update loan outstanding
            loan.outstanding_amount -= amount
            
            # Determine repayment type
            repayment_type = (
                RepaymentType.FULL if loan.outstanding_amount == 0 
                else RepaymentType.PARTIAL
            )

            # Step 5: Create repayment record
            repayment = Repayment(
                loan_id=loan_id,
                amount=amount,
                type=repayment_type,
                status=RepaymentStatus.SUCCESS,
                idempotency_key=idempotency_key
            )
            db.add(repayment)
            db.flush()  # Get repayment ID

            # Step 6: Create transaction ledger entry
            TransactionService.create_transaction(
                db=db,
                user_id=user_id,
                amount=amount,
                transaction_type=TransactionType.DEBIT,
                source=TransactionSource.EMI_PAYMENT,
                reference_id=str(repayment.id),
                description=f"Repayment for loan #{loan_id}"
            )

            # Step 7: Close loan if fully paid
            if loan.outstanding_amount == 0:
                loan.status = LoanStatus.CLOSED

            # Commit entire transaction
            db.commit()
            db.refresh(repayment)
            db.refresh(loan)
            
            return repayment, loan

        except IntegrityError as e:
            db.rollback()
            # Idempotency key violation - return existing
            if "idempotency_key" in str(e):
                existing = (
                    db.query(Repayment)
                    .filter(Repayment.idempotency_key == idempotency_key)
                    .first()
                )
                if existing:
                    loan = LoanService.get_loan_by_id(db, existing.loan_id)
                    return existing, loan
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Repayment failed: {str(e)}"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Repayment failed: {str(e)}"
            )

    @staticmethod
    def get_loan_repayments(db: Session, loan_id: int) -> list[Repayment]:
        """Get all repayments for a loan"""
        return (
            db.query(Repayment)
            .filter(Repayment.loan_id == loan_id)
            .order_by(Repayment.created_at.desc())
            .all()
        )

    @staticmethod
    def calculate_emi_schedule(
        principal: Decimal,
        annual_rate: Decimal,
        tenure_months: int
    ) -> dict:
        """
        Calculate EMI and total interest
        
        Returns schedule information for display
        """
        emi = LoanService.calculate_emi(principal, annual_rate, tenure_months)
        total_amount = emi * tenure_months
        total_interest = total_amount - principal

        return {
            "emi_amount": emi,
            "total_interest": total_interest,
            "total_amount": total_amount,
            "tenure_months": tenure_months
        }
