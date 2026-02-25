from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.loan import (
    LoanCreate, 
    LoanResponse, 
    LoanApprovalRequest, 
    EMICalculation
)
from app.services.loan_service import LoanService
from app.auth.dependencies import get_current_user, require_admin
from typing import List
from decimal import Decimal

router = APIRouter(prefix="/api/loans", tags=["Loans"])


@router.post("/apply", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def apply_for_loan(
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply for a loan
    
    Checks eligibility based on:
    - Maximum loan amount
    - Wallet activity
    - Active loan count
    """
    loan = LoanService.apply_for_loan(
        db=db,
        user_id=current_user.id,
        principal_amount=loan_data.principal_amount,
        tenure_months=loan_data.tenure_months,
        interest_rate=loan_data.interest_rate
    )
    return LoanResponse.model_validate(loan)


@router.get("/my-loans", response_model=List[LoanResponse])
def get_my_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all loans for current user"""
    loans = LoanService.get_user_loans(db, current_user.id)
    return [LoanResponse.model_validate(loan) for loan in loans]


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan_details(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get loan details"""
    loan = LoanService.get_loan_by_id(db, loan_id)
    
    # Users can only see their own loans
    if loan.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this loan"
        )
    
    return LoanResponse.model_validate(loan)


@router.post("/calculate-emi", response_model=EMICalculation)
def calculate_emi(
    loan_data: LoanCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate EMI without applying for loan
    
    Useful for users to see what their EMI would be
    """
    from app.services.repayment_service import RepaymentService
    
    interest_rate = loan_data.interest_rate or LoanService.DEFAULT_INTEREST_RATE
    
    schedule = RepaymentService.calculate_emi_schedule(
        principal=loan_data.principal_amount,
        annual_rate=interest_rate,
        tenure_months=loan_data.tenure_months
    )
    
    return EMICalculation(**schedule)


# Admin endpoints
@router.get("/admin/pending", response_model=List[LoanResponse])
def get_pending_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all pending loan applications
    
    Admin only
    """
    loans = LoanService.get_pending_loans(db)
    return [LoanResponse.model_validate(loan) for loan in loans]


@router.post("/admin/approve", response_model=LoanResponse)
def approve_or_reject_loan(
    approval_data: LoanApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Approve or reject a loan application
    
    Admin only
    
    On approval:
    1. Loan status: APPLIED -> APPROVED -> ACTIVE
    2. Amount credited to user's wallet
    3. Transaction recorded in immutable ledger
    
    All operations are atomic (ACID transaction)
    """
    if approval_data.approved:
        loan = LoanService.approve_loan(
            db=db,
            loan_id=approval_data.loan_id,
            admin_id=current_user.id
        )
    else:
        loan = LoanService.reject_loan(
            db=db,
            loan_id=approval_data.loan_id,
            admin_id=current_user.id,
            reason=approval_data.rejection_reason or ""
        )
    
    return LoanResponse.model_validate(loan)
