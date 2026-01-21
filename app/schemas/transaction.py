from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from app.models.transaction import TransactionType, TransactionSource


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    type: TransactionType
    source: TransactionSource
    reference_id: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
