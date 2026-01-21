# 🏦 Loan Lifecycle & Wallet Backend System

A **production-grade fintech lending platform** built as a monolithic backend system managing loan applications, wallet balances, EMI repayments, and immutable transaction ledgers with strong consistency guarantees. **Now with a dynamic frontend UI!**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ACID-blue)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow)](https://www.python.org/)

---

## ✨ New: Interactive Frontend

This system now includes a **modern, responsive web frontend** for complete user interaction:

- 🔐 **User Authentication** - Register, login, and secure session management
- 💰 **Real-time Wallet** - Live balance updates after every transaction
- 📝 **Loan Application** - Apply for loans with dynamic EMI calculator
- 💳 **Repayment Portal** - Make payments with instant feedback
- 📊 **Transaction History** - View all wallet activities with color-coded amounts
- 👨‍💼 **Admin Dashboard** - Approve/reject loans and monitor system

**See [Frontend Guide](frontend/README.md) for complete documentation!**

---

## 🎯 Business Problem

Modern fintech lenders (like Branch, MoneyLion, Dave) need robust systems to:

1. **Manage loan lifecycles** - From application through approval, disbursement, and closure
2. **Track money flows** - Every rupee/dollar must be accounted for with audit trails
3. **Prevent fraud** - Idempotent operations, transaction isolation, balance constraints
4. **Maintain consistency** - ACID guarantees across wallet updates, loan changes, and ledger entries
5. **Support reconciliation** - Immutable transaction ledger for financial audits

This system demonstrates **real-world fintech engineering principles** rather than toy CRUD APIs.

---

## 🏗️ System Architecture

```
┌─────────────┐
│   Client    │
│  (Mobile/   │
│    Web)     │
└──────┬──────┘
       │
       │ HTTPS + JWT
       │
┌──────▼──────────────────────────────────────┐
│         FastAPI Monolith                     │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │   Authentication Layer (JWT)         │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │   Business Logic Services            │   │
│  │                                      │   │
│  │  • Loan Service                      │   │
│  │  • Wallet Service                    │   │
│  │  • Repayment Service                 │   │
│  │  • Transaction Service (Ledger)      │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │   Data Access Layer (ORM)            │   │
│  └──────────────────────────────────────┘   │
└──────┬───────────────────────────────────────┘
       │
       │ ACID Transactions
       │
┌──────▼──────────────────────────────────────┐
│         PostgreSQL Database                  │
│                                              │
│  • Users & Wallets                           │
│  • Loans & Repayments                        │
│  • Immutable Transaction Ledger              │
└──────────────────────────────────────────────┘
```

---

## 🧠 Core Domain Model

### State Transition Diagram

```
LOAN LIFECYCLE:
                                    ┌──────────┐
                                    │ APPLIED  │
                                    └─────┬────┘
                                          │
                         ┌────────────────┴────────────────┐
                         │                                 │
                    ADMIN APPROVES                   ADMIN REJECTS
                         │                                 │
                    ┌────▼────┐                      ┌─────▼────┐
                    │APPROVED │                      │ REJECTED │
                    └────┬────┘                      └──────────┘
                         │
                 DISBURSE TO WALLET
                         │
                    ┌────▼────┐
                    │ ACTIVE  │
                    └────┬────┘
                         │
                   EMI PAYMENTS
                         │
                ┌────────┴─────────┐
                │                  │
         PARTIAL PAYMENT    FULL PAYMENT
                │                  │
            (continues)       ┌────▼────┐
                              │ CLOSED  │
                              └─────────┘
```

### Money Flow Guarantees

**Every financial operation follows this pattern:**

```
1. START TRANSACTION
2. Validate business rules
3. Update wallet balance (credit/debit)
4. Update loan/repayment state
5. CREATE IMMUTABLE LEDGER ENTRY
6. COMMIT TRANSACTION
```

**If any step fails, ALL steps rollback** (ACID guarantee)

---

## 📊 Database Schema

### Core Tables

```sql
users
├── id (PK)
├── name
├── email (UNIQUE)
├── hashed_password
└── role (USER | ADMIN)

wallets
├── user_id (PK, FK → users)
└── balance (CHECK: balance >= 0)

loans
├── id (PK)
├── user_id (FK → users)
├── principal_amount
├── tenure_months
├── interest_rate
├── status (APPLIED | APPROVED | ACTIVE | CLOSED | REJECTED)
├── outstanding_amount
├── created_at
└── updated_at

repayments
├── id (PK)
├── loan_id (FK → loans)
├── amount
├── type (PARTIAL | FULL)
├── status (SUCCESS | FAILED | PENDING)
├── idempotency_key (UNIQUE) ← Prevents duplicate payments
└── created_at

transactions (IMMUTABLE LEDGER)
├── id (PK)
├── user_id (FK → users)
├── amount
├── type (CREDIT | DEBIT)
├── source (LOAN_DISBURSEMENT | EMI_PAYMENT | WALLET_TOPUP)
├── reference_id (loan_id or repayment_id)
├── description
└── created_at (INDEXED)
```

### Why This Design Matters

1. **Wallet Constraint**: `CHECK (balance >= 0)` prevents overdrafts at database level
2. **Idempotency Key**: Prevents duplicate payments if client retries
3. **Immutable Ledger**: `transactions` table has NO UPDATE or DELETE operations
4. **Foreign Keys**: Ensure referential integrity across entities

---

## 🔐 Security & Authentication

### JWT-Based Authentication

```
1. User registers → Account + Wallet created
2. User logs in → JWT token issued
3. Token contains: {user_id, role, expiry}
4. All protected endpoints require valid token
5. Admin endpoints require ADMIN role
```

### Role-Based Access Control (RBAC)

| Role  | Permissions |
|-------|-------------|
| USER  | Apply for loans, view own loans, make repayments, check wallet |
| ADMIN | Approve/reject loans, view all pending applications |

---

## ⚙️ Core Features Implementation

### 1️⃣ Loan Application

```python
# Eligibility checks performed:
- Maximum loan amount (₹5,00,000)
- Active loan limit (max 2 concurrent loans)
- Wallet activity (mock rule)

# EMI calculated using reducing balance method:
EMI = [P × R × (1+R)^N] / [(1+R)^N - 1]
Where:
  P = Principal
  R = Monthly interest rate (annual/12/100)
  N = Tenure in months
```

### 2️⃣ Loan Approval (CRITICAL)

**ACID Transaction performing:**

```python
BEGIN TRANSACTION:
  1. Update loan.status = APPROVED
  2. Credit wallet.balance += principal_amount
  3. Create transaction record (type=CREDIT, source=LOAN_DISBURSEMENT)
  4. Update loan.status = ACTIVE
COMMIT TRANSACTION

If any step fails → ROLLBACK all changes
```

### 3️⃣ EMI Repayment (with Idempotency)

**Idempotent Design:**

```python
# Client generates UUID: idempotency_key = "abc-123-xyz"

BEGIN TRANSACTION:
  1. Check if idempotency_key exists → return existing result
  2. Validate sufficient wallet balance
  3. Debit wallet.balance -= payment_amount
  4. Update loan.outstanding_amount -= payment_amount
  5. Create repayment record (with idempotency_key)
  6. Create transaction record (type=DEBIT, source=EMI_PAYMENT)
  7. If outstanding = 0 → loan.status = CLOSED
COMMIT TRANSACTION
```

**If client retries with same key → returns original result without re-processing**

### 4️⃣ Transaction Ledger (Source of Truth)

**Immutable by Design:**

```python
# Every money movement creates a transaction entry
# NO UPDATE or DELETE operations allowed
# Provides complete audit trail for reconciliation

Example ledger entries:
[
  {id: 1, user: 5, type: CREDIT, amount: 50000, source: LOAN_DISBURSEMENT},
  {id: 2, user: 5, type: DEBIT, amount: 5234, source: EMI_PAYMENT},
  {id: 3, user: 5, type: DEBIT, amount: 5234, source: EMI_PAYMENT}
]

# Balance verification:
wallet.balance = SUM(CREDITS) - SUM(DEBITS)
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip
- Modern web browser (for frontend)

### Quick Start (Automated)

```bash
# Run the automated setup script
chmod +x setup.sh
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Setup PostgreSQL database
- Create tables
- Seed test data (admin + 2 users)
- Run tests

### Manual Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd loan-lifecycle-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

```bash
# Create database
createdb loan_db

# Or using psql
psql -U postgres
CREATE DATABASE loan_db;
\q
```

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/loan_db
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. Run Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Backend will be available at: **http://localhost:8000**

### 7. Run Frontend (Optional but Recommended)

Open a **new terminal window**:

```bash
cd frontend
./start-frontend.sh

# Or manually:
python3 serve.py
```

Frontend will be available at: **http://localhost:3000**

**Now open your browser and visit:**
- **Frontend UI**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs

**Test Credentials:**
- Admin: `admin@example.com` / `admin123`
- User 1: `user1@example.com` / `user123`
- User 2: `user2@example.com` / `user123`

📖 **See [Frontend Guide](frontend/README.md) for detailed usage instructions!**

### 8. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📖 API Usage Examples

### Complete User Journey

#### 1. Register User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123",
    "role": "USER"
  }'

# Response: JWT token + user details
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "USER"
  }
}
```

#### 2. Check Wallet Balance

```bash
curl -X GET http://localhost:8000/api/wallet/balance \
  -H "Authorization: Bearer <token>"

# Response:
{
  "user_id": 1,
  "balance": "0.00"
}
```

#### 3. Apply for Loan

```bash
curl -X POST http://localhost:8000/api/loans/apply \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "principal_amount": 100000,
    "tenure_months": 12,
    "interest_rate": 12.0
  }'

# Response:
{
  "id": 1,
  "user_id": 1,
  "principal_amount": "100000.00",
  "tenure_months": 12,
  "interest_rate": "12.00",
  "status": "APPLIED",
  "outstanding_amount": "112000.00",
  "created_at": "2026-01-20T10:00:00"
}
```

#### 4. Admin Approves Loan

```bash
# Login as admin first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=adminpass"

# Approve loan
curl -X POST http://localhost:8000/api/loans/admin/approve \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "loan_id": 1,
    "approved": true
  }'

# Response:
{
  "id": 1,
  "status": "ACTIVE",
  "outstanding_amount": "112000.00"
}
```

#### 5. Check Wallet (After Disbursement)

```bash
curl -X GET http://localhost:8000/api/wallet/balance \
  -H "Authorization: Bearer <token>"

# Response:
{
  "user_id": 1,
  "balance": "100000.00"  # Credited!
}
```

#### 6. Make EMI Payment

```bash
curl -X POST http://localhost:8000/api/repayments/make-payment \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "loan_id": 1,
    "amount": 9333.33,
    "idempotency_key": "payment-uuid-12345"
  }'

# Response:
{
  "repayment": {
    "id": 1,
    "loan_id": 1,
    "amount": "9333.33",
    "type": "PARTIAL",
    "status": "SUCCESS"
  },
  "new_outstanding": "102666.67",
  "loan_closed": false
}
```

#### 7. View Transaction Ledger

```bash
curl -X GET http://localhost:8000/api/wallet/transactions \
  -H "Authorization: Bearer <token>"

# Response: Complete audit trail
[
  {
    "id": 1,
    "user_id": 1,
    "amount": "100000.00",
    "type": "CREDIT",
    "source": "LOAN_DISBURSEMENT",
    "reference_id": "1",
    "created_at": "2026-01-20T10:05:00"
  },
  {
    "id": 2,
    "user_id": 1,
    "amount": "9333.33",
    "type": "DEBIT",
    "source": "EMI_PAYMENT",
    "reference_id": "1",
    "created_at": "2026-01-20T11:00:00"
  }
]
```

---

## 🧪 Testing Scenarios

### Scenario 1: Double Disbursement Prevention

```bash
# Admin approves loan twice
curl -X POST .../admin/approve -d '{"loan_id": 1, "approved": true}'
curl -X POST .../admin/approve -d '{"loan_id": 1, "approved": true}'

# Result: Second call returns existing loan, no duplicate disbursement
```

### Scenario 2: Insufficient Balance Prevention

```bash
# Try to pay more than wallet balance
curl -X POST .../repayments/make-payment \
  -d '{"loan_id": 1, "amount": 999999, "idempotency_key": "unique-1"}'

# Result: HTTP 400 - "Insufficient balance"
```

### Scenario 3: Idempotent Repayment

```bash
# Make payment
curl -X POST .../repayments/make-payment \
  -d '{"loan_id": 1, "amount": 5000, "idempotency_key": "payment-abc"}'

# Client retries with same key
curl -X POST .../repayments/make-payment \
  -d '{"loan_id": 1, "amount": 5000, "idempotency_key": "payment-abc"}'

# Result: Same response, no duplicate debit
```

---

## 🛡️ Production Considerations

### What's Implemented

✅ ACID transactions for money flows  
✅ Idempotency keys for payment safety  
✅ Database constraints (non-negative balance)  
✅ JWT authentication with role-based access  
✅ Immutable transaction ledger  
✅ Proper error handling and validation  
✅ State machine for loan lifecycle  

### What's Mocked (For Demo)

🔶 Payment gateway integration (use Stripe/Razorpay in production)  
🔶 Credit scoring (integrate with credit bureaus)  
🔶 SMS/Email notifications (use Twilio/SendGrid)  
🔶 KYC verification (use third-party services)  

### Production Enhancements Needed

1. **Observability**
   - Structured logging (JSON logs)
   - APM (New Relic, DataDog)
   - Metrics (Prometheus)

2. **Security**
   - Rate limiting (Redis + Slowapi)
   - Input sanitization (already using Pydantic)
   - Secret management (AWS Secrets Manager)

3. **Scalability**
   - Database connection pooling (PgBouncer)
   - Caching (Redis for wallet balances)
   - Background jobs (Celery for notifications)

4. **Database**
   - Use Alembic for migrations (not raw init_db)
   - Database replicas for read scaling
   - Partitioning for transaction table

---

## 📁 Project Structure

```
loan-lifecycle-backend/
│
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration & session management
│   │
│   ├── auth/                   # Authentication layer
│   │   ├── jwt.py              # JWT token creation & verification
│   │   └── dependencies.py     # Auth dependencies for routes
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py             # User model
│   │   ├── wallet.py           # Wallet model (with balance constraint)
│   │   ├── loan.py             # Loan model (with status enum)
│   │   ├── repayment.py        # Repayment model (with idempotency)
│   │   └── transaction.py      # Transaction ledger (immutable)
│   │
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── user.py
│   │   ├── wallet.py
│   │   ├── loan.py
│   │   └── repayment.py
│   │
│   ├── services/               # Business logic layer
│   │   ├── loan_service.py         # Loan application, approval, EMI calc
│   │   ├── wallet_service.py       # Wallet credit/debit operations
│   │   ├── repayment_service.py    # Repayment processing
│   │   └── transaction_service.py  # Ledger management
│   │
│   └── routers/                # API endpoints
│       ├── auth.py             # /api/auth/* - Register, login
│       ├── loan.py             # /api/loans/* - Apply, approve, list
│       ├── wallet.py           # /api/wallet/* - Balance, transactions
│       └── repayment.py        # /api/repayments/* - Pay EMI
│
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore
└── README.md                   # This file
```

---

## 🎓 Key Learning Outcomes

### Fintech Engineering Concepts

1. **ACID Transactions** - Understanding why atomicity matters in money flows
2. **Idempotency** - Preventing duplicate payments in distributed systems
3. **State Machines** - Managing loan lifecycle transitions safely
4. **Audit Trails** - Immutable ledgers for reconciliation
5. **Constraint Enforcement** - Using database constraints for invariants

### Software Design Patterns

1. **Service Layer Pattern** - Business logic separated from API layer
2. **Repository Pattern** - Data access abstraction
3. **Dependency Injection** - FastAPI's dependency system
4. **DTO Pattern** - Pydantic schemas for data validation

---

## 💼 Resume-Ready Project Summary

**Built a production-grade fintech lending backend** handling loan applications, wallet management, and EMI repayments with:

- **Strong consistency guarantees** using PostgreSQL ACID transactions
- **Idempotent payment processing** preventing duplicate charges
- **Immutable transaction ledger** for complete audit trails
- **JWT-based authentication** with role-based access control
- **EMI calculation engine** using reducing balance method
- **State machine** for loan lifecycle management (Applied → Approved → Active → Closed)

**Tech Stack**: FastAPI, PostgreSQL, SQLAlchemy, JWT, Pydantic

**Key Achievement**: Ensured zero data inconsistency through proper transaction boundaries and database constraints, demonstrating understanding of real-world fintech requirements.

---

## 📞 Support & Contribution

This is a demonstration project showcasing fintech backend engineering principles.

### Next Steps for Production

1. Add comprehensive test suite (pytest, pytest-asyncio)
2. Implement Alembic database migrations
3. Add API rate limiting
4. Integrate real payment gateway
5. Add background job processing (Celery)
6. Implement proper logging and monitoring
7. Add CI/CD pipeline

---

## 📜 License

MIT License - Free to use for learning and portfolio purposes

---

## 🙏 Acknowledgments

Built following industry best practices from:
- Branch International's engineering blog
- Stripe API design principles
- PostgreSQL transaction isolation documentation
- FastAPI production deployment guides

---

**Note**: This is a learning project demonstrating fintech backend concepts. Not recommended for production use without additional security hardening, testing, and compliance measures.
