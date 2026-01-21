from sqlalchemy import Column, Integer, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    balance = Column(Numeric(15, 2), default=0.00, nullable=False)

    # Constraint: balance cannot be negative
    __table_args__ = (
        CheckConstraint('balance >= 0', name='positive_balance'),
    )

    # Relationships
    user = relationship("User", back_populates="wallet")
