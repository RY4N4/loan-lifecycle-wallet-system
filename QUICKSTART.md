# 🚀 Quick Start Guide

## Setup Checklist

### Prerequisites ✅

- [ ] Python 3.9 or higher installed
- [ ] PostgreSQL 12 or higher installed and running
- [ ] pip package manager available
- [ ] Git installed (optional, for version control)

---

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend
```

### 2. Run Setup Script (Automated)

```bash
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create `.env` file

### 3. Configure Database

Edit `.env` file with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/loan_db
SECRET_KEY=generate-a-secure-random-key-here
```

**Generate a secure secret key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Create PostgreSQL Database

```bash
# Option 1: Using createdb command
createdb loan_db

# Option 2: Using psql
psql -U postgres
CREATE DATABASE loan_db;
\q
```

### 5. Seed Sample Data (Optional but Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Run seed script
python seed_data.py
```

This creates:
- Admin user: `admin@example.com` / `admin123`
- Test users: `john@example.com` / `password123`

### 6. Start the Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the server
uvicorn app.main:app --reload
```

The server will start at: **http://localhost:8000**

---

## Verify Installation

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "services": {
    "auth": "operational",
    "loans": "operational",
    "wallet": "operational",
    "repayments": "operational"
  }
}
```

### 2. Access API Documentation

Open in browser: **http://localhost:8000/docs**

You should see the Swagger UI with all available endpoints.

---

## Test the API

### Option 1: Using Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Click on `/api/auth/register`
3. Click "Try it out"
4. Fill in the form and execute
5. Copy the `access_token` from response
6. Click "Authorize" button (top right)
7. Paste token and authorize
8. Now you can test all other endpoints!

### Option 2: Using Python Script (Automated)

```bash
# Install requests library (if not already installed)
pip install requests

# Run the test script
python test_api.py
```

This will run a complete user journey:
- Register user
- Apply for loan
- Admin approves
- User makes repayment
- View transaction history

### Option 3: Using cURL (Manual)

See `README.md` for detailed cURL examples.

---

## Common Issues & Solutions

### Issue 1: Database Connection Error

**Error:** `could not connect to server: Connection refused`

**Solution:**
- Ensure PostgreSQL is running: `pg_ctl status`
- Start PostgreSQL: `brew services start postgresql` (Mac) or `sudo systemctl start postgresql` (Linux)
- Check DATABASE_URL in `.env` has correct credentials

### Issue 2: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Issue 3: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 4: Database Does Not Exist

**Error:** `database "loan_db" does not exist`

**Solution:**
```bash
createdb loan_db
```

---

## Project Structure

```
loan-lifecycle-backend/
├── app/
│   ├── main.py              ← FastAPI application entry
│   ├── database.py          ← Database configuration
│   ├── auth/                ← JWT authentication
│   ├── models/              ← Database models
│   ├── schemas/             ← Pydantic validation
│   ├── services/            ← Business logic
│   └── routers/             ← API endpoints
├── requirements.txt         ← Python dependencies
├── .env                     ← Environment variables (create from .env.example)
├── seed_data.py            ← Sample data generator
├── test_api.py             ← API testing script
└── README.md               ← Full documentation
```

---

## Next Steps

### For Development

1. **Read the Documentation**
   - `README.md` - Complete system documentation
   - `ARCHITECTURE.md` - Design decisions and patterns

2. **Explore the Code**
   - Start with `app/main.py` - Application entry point
   - Check `app/routers/` - API endpoints
   - Review `app/services/` - Business logic

3. **Run Tests**
   - Execute `test_api.py` to see complete flow
   - Try different scenarios via Swagger UI

### For Production

1. **Security Hardening**
   - Change SECRET_KEY to a strong random value
   - Enable HTTPS/TLS
   - Set up proper CORS origins
   - Implement rate limiting

2. **Database Migrations**
   - Set up Alembic for schema migrations
   - Use proper migration workflow

3. **Monitoring**
   - Add logging framework (structured JSON logs)
   - Set up error tracking (Sentry)
   - Configure APM (New Relic/DataDog)

4. **Deployment**
   - Use gunicorn/uvicorn workers
   - Set up reverse proxy (Nginx)
   - Configure connection pooling (PgBouncer)
   - Enable database backups

---

## Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run server
uvicorn app.main:app --reload

# Run server on different port
uvicorn app.main:app --reload --port 8001

# Run with multiple workers (production)
uvicorn app.main:app --workers 4

# Deactivate virtual environment
deactivate

# Check Python version
python --version

# Check PostgreSQL version
psql --version
```

---

## Support

If you encounter issues:

1. Check the [Common Issues](#common-issues--solutions) section
2. Review the full `README.md` documentation
3. Verify all prerequisites are installed
4. Ensure `.env` is configured correctly
5. Check that PostgreSQL is running

---

## Features Overview

✅ **Implemented**
- User registration and JWT authentication
- Loan application with eligibility checks
- Admin loan approval with ACID transactions
- Wallet balance management
- EMI-based repayments with idempotency
- Immutable transaction ledger
- Role-based access control
- Complete API documentation

🚀 **Production-Ready Features**
- ACID transaction guarantees
- Idempotent payment processing
- Database-level constraints
- Proper error handling
- Security best practices

---

**🎉 You're all set! Happy coding!**

For detailed API documentation and examples, see `README.md`.
For architecture details and design decisions, see `ARCHITECTURE.md`.
