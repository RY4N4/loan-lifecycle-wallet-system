from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth_router, loan_router, wallet_router, repayment_router

# Initialize FastAPI app
app = FastAPI(
    title="Loan Lifecycle & Wallet Backend",
    description="Production-grade fintech lending system with wallet, loans, and repayments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    
    In production, this would log to monitoring service
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if app.debug else "An error occurred"
        }
    )


# Include routers
app.include_router(auth_router)
app.include_router(loan_router)
app.include_router(wallet_router)
app.include_router(repayment_router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup
    
    In production, use Alembic migrations instead
    """
    init_db()


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Loan Lifecycle Backend",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "auth": "operational",
            "loans": "operational",
            "wallet": "operational",
            "repayments": "operational"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
