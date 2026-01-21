from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
from app.models.repayment import RepaymentType, RepaymentStatus


class RepaymentCreate(BaseModel):
    loan_id: int
    amount: Decimal = Field(..., gt=0)
    idempotency_key: str = Field(..., min_length=1)  # Client-generated unique key


class RepaymentResponse(BaseModel):
    id: int
    loan_id: int
    amount: Decimal
    type: RepaymentType
    status: RepaymentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class RepaymentResult(BaseModel):
    repayment: RepaymentResponse
    new_outstanding: Decimal
    loan_closed: bool
