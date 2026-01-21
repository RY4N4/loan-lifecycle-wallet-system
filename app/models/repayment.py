from sqlalchemy import Column, Integer, ForeignKey, Numeric, Enum as SQLEnum, DateTime, String
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class RepaymentType(str, enum.Enum):
    PARTIAL = "PARTIAL"
    FULL = "FULL"


class RepaymentStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"


class Repayment(Base):
    __tablename__ = "repayments"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    type = Column(SQLEnum(RepaymentType), nullable=False)
    status = Column(SQLEnum(RepaymentStatus), default=RepaymentStatus.PENDING, nullable=False)
    idempotency_key = Column(String, unique=True, index=True)  # Prevent duplicate payments
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    loan = relationship("Loan", back_populates="repayments")
