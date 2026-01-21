# Import all models here for Alembic migrations
from app.models.user import User, UserRole
from app.models.wallet import Wallet
from app.models.loan import Loan, LoanStatus
from app.models.repayment import Repayment, RepaymentType, RepaymentStatus
from app.models.transaction import Transaction, TransactionType, TransactionSource

__all__ = [
    "User",
    "UserRole",
    "Wallet",
    "Loan",
    "LoanStatus",
    "Repayment",
    "RepaymentType",
    "RepaymentStatus",
    "Transaction",
    "TransactionType",
    "TransactionSource",
]
