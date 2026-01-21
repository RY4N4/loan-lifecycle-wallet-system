from sqlalchemy.orm import Session
from app.models.loan import Loan, LoanStatus
from app.models.transaction import TransactionType, TransactionSource
from app.services.wallet_service import WalletService
from app.services.transaction_service import TransactionService
from decimal import Decimal
from fastapi import HTTPException, status
from typing import List
import math


class LoanService:
    """
    Loan Service - Core lending business logic
    
    Handles:
    1. Loan application with eligibility checks
    2. Loan approval and disbursement (ACID transaction)
    3. EMI calculations
    4. Loan closure
    """

    # Business rules
    MAX_LOAN_AMOUNT = Decimal("500000.00")  # 5 lakh max
    DEFAULT_INTEREST_RATE = Decimal("12.00")  # 12% annual
    MIN_TENURE = 1
    MAX_TENURE = 60  # 5 years

    @staticmethod
    def calculate_emi(
        principal: Decimal,
        annual_rate: Decimal,
        tenure_months: int
    ) -> Decimal:
        """
        Calculate EMI using reducing balance method
        
        Formula: EMI = [P x R x (1+R)^N]/[(1+R)^N-1]
        Where:
        P = Principal
        R = Monthly interest rate (annual/12/100)
        N = Tenure in months
        """
        if annual_rate == 0:
            return principal / tenure_months

        monthly_rate = float(annual_rate) / 12 / 100
        emi = (
            float(principal) * monthly_rate * math.pow(1 + monthly_rate, tenure_months)
        ) / (math.pow(1 + monthly_rate, tenure_months) - 1)
        
        return Decimal(str(round(emi, 2)))

    @staticmethod
    def check_eligibility(
        db: Session,
        user_id: int,
        requested_amount: Decimal
    ) -> tuple[bool, str]:
        """
        Mock eligibility check
        
        Production rules would include:
        - Credit score
        - Income verification
        - Existing loan count
        - Repayment history
        """
        # Check max loan limit
        if requested_amount > LoanService.MAX_LOAN_AMOUNT:
            return False, f"Loan amount exceeds maximum limit of {LoanService.MAX_LOAN_AMOUNT}"

        # Check wallet activity (mock rule)
        has_activity = WalletService.check_wallet_activity(db, user_id)
        if not has_activity:
            return False, "Insufficient wallet activity"

        # Check active loans
        active_loans = (
            db.query(Loan)
            .filter(
                Loan.user_id == user_id,
                Loan.status.in_([LoanStatus.ACTIVE, LoanStatus.APPROVED])
            )
            .count()
        )

        if active_loans >= 2:
            return False, "Maximum active loan limit reached"

        return True, "Eligible"

    @staticmethod
    def apply_for_loan(
        db: Session,
        user_id: int,
        principal_amount: Decimal,
        tenure_months: int,
        interest_rate: Decimal = None
    ) -> Loan:
        """
        Create a loan application
        
        State: APPLIED
        """
        # Set default interest rate if not provided
        if interest_rate is None:
            interest_rate = LoanService.DEFAULT_INTEREST_RATE

        # Check eligibility
        eligible, message = LoanService.check_eligibility(db, user_id, principal_amount)
        if not eligible:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # Calculate total amount with interest
        emi = LoanService.calculate_emi(principal_amount, interest_rate, tenure_months)
        total_amount = emi * tenure_months

        loan = Loan(
            user_id=user_id,
            principal_amount=principal_amount,
            tenure_months=tenure_months,
            interest_rate=interest_rate,
            status=LoanStatus.APPLIED,
            outstanding_amount=total_amount
        )

        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def approve_loan(
        db: Session,
        loan_id: int,
        admin_id: int
    ) -> Loan:
        """
        Approve loan and disburse to wallet
        
        CRITICAL: This is an ACID transaction
        1. Update loan status: APPLIED -> APPROVED -> ACTIVE
        2. Credit wallet
        3. Create transaction ledger entry
        
        All must succeed or all must fail.
        """
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )

        # Idempotency: If already approved, return existing
        if loan.status in [LoanStatus.APPROVED, LoanStatus.ACTIVE]:
            return loan

        if loan.status != LoanStatus.APPLIED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve loan in {loan.status} state"
            )

        try:
            # Step 1: Update loan status
            loan.status = LoanStatus.APPROVED

            # Step 2: Credit wallet
            WalletService.credit_wallet(
                db,
                user_id=loan.user_id,
                amount=loan.principal_amount
            )

            # Step 3: Create immutable transaction record
            TransactionService.create_transaction(
                db=db,
                user_id=loan.user_id,
                amount=loan.principal_amount,
                transaction_type=TransactionType.CREDIT,
                source=TransactionSource.LOAN_DISBURSEMENT,
                reference_id=str(loan.id),
                description=f"Loan disbursement for loan #{loan.id}"
            )

            # Step 4: Mark loan as active
            loan.status = LoanStatus.ACTIVE

            # Commit entire transaction
            db.commit()
            db.refresh(loan)
            return loan

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Loan approval failed: {str(e)}"
            )

    @staticmethod
    def reject_loan(
        db: Session,
        loan_id: int,
        admin_id: int,
        reason: str = ""
    ) -> Loan:
        """Reject a loan application"""
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )

        if loan.status != LoanStatus.APPLIED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject loan in {loan.status} state"
            )

        loan.status = LoanStatus.REJECTED
        db.commit()
        db.refresh(loan)
        return loan

    @staticmethod
    def get_user_loans(db: Session, user_id: int) -> List[Loan]:
        """Get all loans for a user"""
        return (
            db.query(Loan)
            .filter(Loan.user_id == user_id)
            .order_by(Loan.created_at.desc())
            .all()
        )

    @staticmethod
    def get_loan_by_id(db: Session, loan_id: int) -> Loan:
        """Get loan by ID"""
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )
        return loan

    @staticmethod
    def get_pending_loans(db: Session) -> List[Loan]:
        """Get all pending loan applications (for admin)"""
        return (
            db.query(Loan)
            .filter(Loan.status == LoanStatus.APPLIED)
            .order_by(Loan.created_at.asc())
            .all()
        )
