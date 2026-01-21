from pydantic import BaseModel, Field
from decimal import Decimal


class WalletResponse(BaseModel):
    user_id: int
    balance: Decimal

    class Config:
        from_attributes = True


class WalletBalanceUpdate(BaseModel):
    """For internal use only - not exposed via API"""
    amount: Decimal = Field(..., gt=0)
