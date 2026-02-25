from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, Enum as SQLEnum, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class TransactionSource(str, enum.Enum):
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    EMI_PAYMENT = "EMI_PAYMENT"
    WALLET_TOPUP = "WALLET_TOPUP"


class Transaction(Base):
    """
    IMMUTABLE LEDGER - NO UPDATES ALLOWED
    Every money movement creates a transaction.
    This is the source of truth for all financial operations.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    source = Column(SQLEnum(TransactionSource), nullable=False)
    reference_id = Column(String, index=True)  # loan_id or repayment_id
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="transactions")
