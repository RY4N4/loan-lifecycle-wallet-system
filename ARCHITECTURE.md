# System Architecture & Design Decisions

## Overview

This document explains the architectural decisions, trade-offs, and design patterns used in the Loan Lifecycle Backend system.

---

## Architecture Style: Monolith

### Why Monolith?

**Chosen for:**
- ✅ Simpler deployment (single application)
- ✅ ACID transactions across all operations
- ✅ Lower operational complexity
- ✅ Easier debugging and development
- ✅ No network latency between "services"

**When to migrate to microservices:**
- Different scaling requirements per domain
- Need for polyglot persistence
- Independent deployment cycles required
- Team size exceeds 50+ engineers

---

## Layered Architecture

```
┌─────────────────────────────────────────────┐
│         Presentation Layer                  │
│  (FastAPI Routers - HTTP Request Handlers)  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Business Logic Layer                │
│     (Services - Domain Logic & Rules)       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Data Access Layer                   │
│    (SQLAlchemy Models & Repositories)       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│         Database Layer                      │
│         (PostgreSQL)                        │
└─────────────────────────────────────────────┘
```

### Benefits

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Testability**: Business logic can be tested without HTTP layer
3. **Maintainability**: Changes in one layer don't affect others
4. **Flexibility**: Can swap database or API framework with minimal impact

---

## Design Patterns Used

### 1. Service Layer Pattern

**Location**: `app/services/`

**Purpose**: Encapsulate business logic away from HTTP layer

**Example**:
```python
# ✅ Good: Business logic in service
class LoanService:
    @staticmethod
    def approve_loan(db, loan_id, admin_id):
        # Business rules
        # ACID transaction
        # Multiple table updates
        return loan

# ✅ Router just delegates
@router.post("/admin/approve")
def approve_loan(data, db, current_user):
    return LoanService.approve_loan(db, data.loan_id, current_user.id)
```

### 2. Repository Pattern (via SQLAlchemy)

**Location**: `app/models/`

**Purpose**: Abstract database access

**Example**:
```python
# Models define the schema
class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True)
    # ...

# Services use ORM for queries
loans = db.query(Loan).filter(Loan.status == "ACTIVE").all()
```

### 3. Dependency Injection

**Location**: `app/auth/dependencies.py`

**Purpose**: Inject database sessions, current user, etc.

**Example**:
```python
# Dependencies declared in function signature
def get_my_loans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # db and current_user automatically injected
    return LoanService.get_user_loans(db, current_user.id)
```

### 4. DTO Pattern (Data Transfer Objects)

**Location**: `app/schemas/`

**Purpose**: Validate and serialize data

**Example**:
```python
# Input validation
class LoanCreate(BaseModel):
    principal_amount: Decimal = Field(gt=0, le=1000000)
    tenure_months: int = Field(ge=1, le=60)

# Output serialization
class LoanResponse(BaseModel):
    id: int
    status: LoanStatus
    # ...
```

---

## Data Consistency Guarantees

### ACID Transactions

**Every money movement is wrapped in a transaction:**

```python
try:
    # Multiple operations
    wallet.balance += amount
    loan.status = ACTIVE
    transaction_record = Transaction(...)
    db.add(transaction_record)
    
    db.commit()  # All or nothing
except:
    db.rollback()  # Undo everything
    raise
```

### Database Constraints

**Enforced at DB level (not just application):**

```sql
-- Cannot have negative balance
ALTER TABLE wallets ADD CONSTRAINT positive_balance CHECK (balance >= 0);

-- Unique idempotency keys
ALTER TABLE repayments ADD CONSTRAINT unique_idempotency UNIQUE (idempotency_key);
```

### Immutable Ledger

**Transaction table is append-only:**

- ❌ No UPDATE statements
- ❌ No DELETE statements
- ✅ Only INSERT allowed
- ✅ Complete audit trail

---

## Idempotency Implementation

### Problem

Client makes payment → Network timeout → Retry → Double charge! 💸

### Solution

**Client-generated idempotency keys:**

```python
# Client generates UUID once
idempotency_key = "payment-abc-123-xyz"

# First request
POST /repayments/make-payment
{
  "amount": 5000,
  "idempotency_key": "payment-abc-123-xyz"
}
# → Creates repayment, returns result

# Retry (same key)
POST /repayments/make-payment
{
  "amount": 5000,
  "idempotency_key": "payment-abc-123-xyz"
}
# → Finds existing repayment, returns same result
# → No double charge!
```

**Implementation**:
1. Check if key exists in database
2. If exists, return existing result
3. If not, process payment and store with key
4. Database UNIQUE constraint prevents race conditions

---

## State Machine Design

### Loan State Transitions

```
APPLIED → (approve) → APPROVED → (disburse) → ACTIVE
                                    ↓
        ← (reject)  ← REJECTED   (repay) → CLOSED
```

**Validation rules:**
- Can only approve APPLIED loans
- Can only disburse APPROVED loans
- Can only repay ACTIVE loans
- Cannot reverse CLOSED or REJECTED states

**Enforcement:**
```python
if loan.status != LoanStatus.APPLIED:
    raise HTTPException("Cannot approve loan in this state")
```

---

## Security Architecture

### Authentication Flow

```
1. User provides email + password
   ↓
2. Server validates credentials
   ↓
3. Server generates JWT token
   {
     "sub": user_id,
     "role": "USER",
     "exp": timestamp
   }
   ↓
4. Client includes token in Authorization header
   ↓
5. Server validates token on each request
   ↓
6. If valid, extract user_id and proceed
```

### Authorization

**Role-Based Access Control (RBAC):**

| Endpoint | USER | ADMIN |
|----------|------|-------|
| Apply for loan | ✅ | ✅ |
| View own loans | ✅ | ✅ |
| Approve loans | ❌ | ✅ |
| View all pending | ❌ | ✅ |

**Implementation:**
```python
# Require authentication
def endpoint(current_user: User = Depends(get_current_user)):
    # current_user is injected

# Require admin role
def admin_endpoint(admin: User = Depends(require_admin)):
    # admin is injected (or 403 raised)
```

---

## EMI Calculation Logic

### Formula

```
EMI = [P × R × (1+R)^N] / [(1+R)^N - 1]

Where:
P = Principal amount
R = Monthly interest rate (annual_rate / 12 / 100)
N = Tenure in months
```

### Example Calculation

```
Principal: ₹100,000
Tenure: 12 months
Interest: 12% per annum

R = 12 / 12 / 100 = 0.01
N = 12

EMI = [100000 × 0.01 × (1.01)^12] / [(1.01)^12 - 1]
    = [100000 × 0.01 × 1.1268] / [0.1268]
    = 1126.8 / 0.1268
    = ₹8,884.88

Total = ₹8,884.88 × 12 = ₹106,618.56
Interest = ₹106,618.56 - ₹100,000 = ₹6,618.56
```

---

## Error Handling Strategy

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Resource created |
| 400 | Bad request (validation failure) |
| 401 | Unauthorized (invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 500 | Internal server error |

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### Exception Handling

```python
# Business logic raises HTTPException
if amount > wallet.balance:
    raise HTTPException(
        status_code=400,
        detail="Insufficient balance"
    )

# FastAPI converts to HTTP response
# Client receives proper status code + message
```

---

## Database Design Decisions

### Why PostgreSQL?

**Chosen for:**
- ✅ ACID compliance (critical for money)
- ✅ Referential integrity (foreign keys)
- ✅ CHECK constraints (balance >= 0)
- ✅ UNIQUE constraints (idempotency keys)
- ✅ Excellent JSON support (for future extensibility)
- ✅ Battle-tested for financial applications

### Indexing Strategy

**Indexes created on:**
- Primary keys (automatic)
- Foreign keys (for joins)
- `transactions.created_at` (for time-based queries)
- `transactions.reference_id` (for lookups)
- `repayments.idempotency_key` (for idempotency checks)
- `users.email` (for login queries)

### Normalization Level

**3NF (Third Normal Form):**
- No redundant data
- Each table represents one entity
- Relationships via foreign keys

**Example:**
```
users ← wallet (1:1)
users ← loans (1:N)
loans ← repayments (1:N)
users ← transactions (1:N)
```

---

## Scalability Considerations

### Current Bottlenecks

1. **Database connections**: Limited by PostgreSQL max_connections
2. **Transaction ledger**: Will grow unbounded
3. **Wallet queries**: Hit database on every request

### Future Optimizations

#### 1. Connection Pooling
```
Application → PgBouncer → PostgreSQL
(100 connections) → (20 pool) → (database)
```

#### 2. Read Replicas
```
Writes → Primary DB
Reads → Replica 1, Replica 2, Replica 3
```

#### 3. Caching Layer
```python
# Cache wallet balances
@cache(ttl=60)
def get_wallet_balance(user_id):
    return db.query(Wallet).filter(...)
```

#### 4. Database Partitioning
```sql
-- Partition transaction table by month
CREATE TABLE transactions_2026_01 PARTITION OF transactions
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

---

## Testing Strategy

### Unit Tests
- Test business logic in services
- Mock database connections
- Fast execution (<1s)

### Integration Tests
- Test API endpoints end-to-end
- Use test database
- Verify database state changes

### Test Scenarios

**Critical paths to test:**
1. ✅ Loan approval creates transaction
2. ✅ Insufficient balance blocks repayment
3. ✅ Idempotency prevents double payment
4. ✅ Concurrent approvals don't duplicate disbursement
5. ✅ Negative balance blocked by constraint

---

## Monitoring & Observability

### Metrics to Track (Production)

**Business Metrics:**
- Loan application rate
- Approval rate
- Average disbursement time
- Repayment success rate
- Default rate

**Technical Metrics:**
- API response time (p50, p95, p99)
- Database query time
- Error rate by endpoint
- Active users
- Transaction throughput

**Financial Metrics:**
- Total disbursed amount
- Total repaid amount
- Outstanding loans value
- Revenue (interest collected)

### Logging Strategy

```python
# Structured JSON logs
logger.info(
    "loan_approved",
    extra={
        "loan_id": loan.id,
        "user_id": loan.user_id,
        "amount": loan.principal_amount,
        "admin_id": admin_id
    }
)
```

---

## Deployment Architecture

### Recommended Setup

```
┌─────────────┐
│  Nginx      │ ← Load Balancer
│  (Reverse   │
│   Proxy)    │
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──┐
│App 1│ │App 2│ ← FastAPI instances (gunicorn/uvicorn)
└──┬──┘ └──┬──┘
   └───┬───┘
       │
┌──────▼──────┐
│ PostgreSQL  │ ← Primary database
│             │
│ (+ Replica) │ ← Read replica
└─────────────┘
```

### Environment Variables

**Required:**
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (rotate regularly)
- `ALGORITHM`: JWT algorithm (HS256)

**Optional:**
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token TTL
- `LOG_LEVEL`: Logging verbosity

---

## Compliance Considerations

### PCI DSS (If handling real payments)
- Never store CVV
- Encrypt card numbers
- Use tokenization (Stripe, Razorpay)

### GDPR (If serving EU users)
- Provide data export
- Implement data deletion
- Obtain consent for data processing

### SOC 2 (For enterprise customers)
- Audit logging
- Access controls
- Encryption at rest

---

## Future Enhancements

### Short Term (1-3 months)
1. ✅ Add comprehensive test suite
2. ✅ Implement Alembic migrations
3. ✅ Add API rate limiting
4. ✅ Integrate Sentry for error tracking

### Medium Term (3-6 months)
1. Add mobile app support (OAuth2)
2. Implement recurring payments
3. Add loan restructuring
4. Build analytics dashboard

### Long Term (6-12 months)
1. Machine learning for credit scoring
2. Fraud detection system
3. Multi-currency support
4. Microservices migration (if needed)

---

## Conclusion

This architecture prioritizes:
- ✅ **Correctness** over performance
- ✅ **Simplicity** over premature optimization
- ✅ **Maintainability** over cleverness
- ✅ **Safety** over speed

The system is designed to be understandable, debuggable, and extensible while maintaining the strict guarantees required for financial applications.
