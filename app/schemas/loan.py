from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
from app.models.loan import LoanStatus


class LoanCreate(BaseModel):
    principal_amount: Decimal = Field(..., gt=0, le=1000000)
    tenure_months: int = Field(..., ge=1, le=60)  # Max 5 years
    interest_rate: Optional[Decimal] = Field(None, ge=0, le=50)  # Annual %


class LoanApprovalRequest(BaseModel):
    loan_id: int
    approved: bool
    rejection_reason: Optional[str] = None


class LoanResponse(BaseModel):
    id: int
    user_id: int
    principal_amount: Decimal
    tenure_months: int
    interest_rate: Decimal
    status: LoanStatus
    outstanding_amount: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EMICalculation(BaseModel):
    emi_amount: Decimal
    total_interest: Decimal
    total_amount: Decimal
    tenure_months: int
