from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.repayment import RepaymentCreate, RepaymentResponse, RepaymentResult
from app.services.repayment_service import RepaymentService
from app.auth.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/api/repayments", tags=["Repayments"])


@router.post("/make-payment", response_model=RepaymentResult, status_code=status.HTTP_201_CREATED)
def make_repayment(
    repayment_data: RepaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Make a loan repayment (EMI payment)
    
    CRITICAL FEATURES:
    1. Idempotent: Same idempotency_key returns same result
    2. ACID Transaction: All steps succeed or all fail
    
    Steps:
    1. Validate loan and amount
    2. Debit wallet
    3. Update loan outstanding
    4. Create repayment record
    5. Create transaction ledger entry
    6. Close loan if fully paid
    
    Args:
        idempotency_key: Client-generated unique key (UUID recommended)
    
    Returns:
        RepaymentResult with repayment details and updated loan status
    """
    repayment, loan = RepaymentService.make_repayment(
        db=db,
        user_id=current_user.id,
        loan_id=repayment_data.loan_id,
        amount=repayment_data.amount,
        idempotency_key=repayment_data.idempotency_key
    )
    
    return RepaymentResult(
        repayment=RepaymentResponse.model_validate(repayment),
        new_outstanding=loan.outstanding_amount,
        loan_closed=(loan.outstanding_amount == 0)
    )


@router.get("/loan/{loan_id}", response_model=List[RepaymentResponse])
def get_loan_repayments(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all repayments for a specific loan
    
    Users can only see repayments for their own loans
    """
    from app.services.loan_service import LoanService
    
    # Verify user owns this loan
    loan = LoanService.get_loan_by_id(db, loan_id)
    if loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view repayments for this loan"
        )
    
    repayments = RepaymentService.get_loan_repayments(db, loan_id)
    return [RepaymentResponse.model_validate(r) for r in repayments]
