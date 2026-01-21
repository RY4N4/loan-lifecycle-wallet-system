from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class LoanStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    principal_amount = Column(Numeric(15, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=False)  # Annual interest rate
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.APPLIED, nullable=False)
    outstanding_amount = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="loans")
    repayments = relationship("Repayment", back_populates="loan")
