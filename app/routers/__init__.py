from app.routers.auth import router as auth_router
from app.routers.loan import router as loan_router
from app.routers.wallet import router as wallet_router
from app.routers.repayment import router as repayment_router

__all__ = [
    "auth_router",
    "loan_router",
    "wallet_router",
    "repayment_router",
]
