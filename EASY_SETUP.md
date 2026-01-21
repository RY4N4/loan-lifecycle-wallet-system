# 🚀 Easy Setup Guide - No Errors Guaranteed!

## Option 1: Quick Start with SQLite (Recommended for Testing)

**Perfect for immediate testing without PostgreSQL setup!**

### Step 1: Update .env file

```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend
```

Edit `.env` file and change the DATABASE_URL:
```env
# Comment out PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/loan_db

# Use SQLite instead (no installation needed!)
DATABASE_URL=sqlite:///./loan_app.db

SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 2: Install Dependencies (Clean Install)

```bash
# Deactivate current venv if active
deactivate 2>/dev/null || true

# Remove old venv
rm -rf venv

# Create new venv with system Python (not conda)
/usr/bin/python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies (without psycopg2 for SQLite)
pip install fastapi==0.109.0 \
    uvicorn[standard]==0.27.0 \
    sqlalchemy==2.0.25 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    python-multipart==0.0.6 \
    python-dotenv==1.0.0
```

### Step 3: Initialize Database

```bash
python seed_data.py
```

### Step 4: Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

✅ **Backend running at:** http://localhost:8000

### Step 5: Start Frontend (New Terminal)

```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend/frontend
python3 serve.py
```

✅ **Frontend running at:** http://localhost:3000

### Step 6: Test It!

Open browser: http://localhost:3000

**Login credentials:**
- Admin: `admin@example.com` / `admin123`
- User: `user1@example.com` / `user123`

---

## Option 2: Full Setup with PostgreSQL

**For production-like environment:**

### Step 1: Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Verify installation:**
```bash
psql --version
```

### Step 2: Create Database

```bash
# Create database
createdb loan_db

# Or using psql
psql postgres
CREATE DATABASE loan_db;
\q
```

### Step 3: Setup Virtual Environment

```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend

# Remove old venv
rm -rf venv

# Create new venv
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**If psycopg2-binary fails:**
```bash
# Try this workaround
brew install postgresql
pip install psycopg2-binary --no-binary psycopg2-binary
```

### Step 4: Configure .env

```env
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/loan_db
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace `YOUR_USERNAME` with your macOS username (usually no password needed locally).

### Step 5: Initialize Database

```bash
python seed_data.py
```

### Step 6: Run Servers

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python3 serve.py
```

---

## 🆘 Troubleshooting

### Error: "No module named 'psycopg2'"

**Solution:** Use SQLite (Option 1) or install PostgreSQL properly:
```bash
brew install postgresql
pip install psycopg2-binary
```

### Error: "Could not connect to database"

**Solution:** Check PostgreSQL is running:
```bash
brew services list | grep postgresql
# Should show "started"

# If not:
brew services start postgresql@14
```

### Error: "Port 8000 already in use"

**Solution:** Kill the process:
```bash
lsof -ti:8000 | xargs kill -9
```

### Error: "Port 3000 already in use"

**Solution:** Kill the process or use different port:
```bash
lsof -ti:3000 | xargs kill -9
# Or edit frontend/serve.py and change PORT = 3001
```

### Virtual Environment Issues

**Solution:** Use system Python:
```bash
deactivate 2>/dev/null || true
rm -rf venv
/usr/bin/python3 -m venv venv
source venv/bin/activate
```

### Conda Interference

**Solution:** Deactivate conda first:
```bash
conda deactivate
# Then follow setup steps
```

---

## ✅ Verification Checklist

- [ ] Backend starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:3000
- [ ] Can login with test credentials
- [ ] Can see wallet balance
- [ ] Can apply for loan
- [ ] EMI calculator works
- [ ] Admin can approve loans
- [ ] Can make repayments

---

## 🎯 Quick Commands Reference

```bash
# Start everything (after initial setup)
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend

# Terminal 1
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 (new window)
cd frontend
python3 serve.py
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📝 Environment Variables Explained

```env
# SQLite (easiest)
DATABASE_URL=sqlite:///./loan_app.db

# PostgreSQL (production)
DATABASE_URL=postgresql://username:password@localhost:5432/loan_db

# JWT Settings
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 🚀 One-Line Setup (SQLite)

```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend && \
rm -rf venv && \
/usr/bin/python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install fastapi uvicorn[standard] sqlalchemy pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart python-dotenv && \
echo 'DATABASE_URL=sqlite:///./loan_app.db
SECRET_KEY=dev-secret-key-change-in-production-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30' > .env && \
python seed_data.py && \
echo "✅ Setup complete! Now run: uvicorn app.main:app --reload --port 8000"
```

Then in a new terminal:
```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend/frontend && python3 serve.py
```

---

## 💡 Pro Tips

1. **Use SQLite for development** - No database installation needed!
2. **Open 2 terminal windows** - One for backend, one for frontend
3. **Check API docs first** - Visit http://localhost:8000/docs to verify backend
4. **Use test credentials** - They're pre-loaded in the database
5. **Clear browser cache** - If frontend doesn't update, hard refresh (Cmd+Shift+R)

---

## 🎉 Success Indicators

When everything is working, you should see:

**Backend Terminal:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using WatchFiles
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Frontend Terminal:**
```
╔════════════════════════════════════════════╗
║   Frontend Server Running                 ║
╠════════════════════════════════════════════╣
║   URL: http://localhost:3000            ║
║   Press Ctrl+C to stop                     ║
╚════════════════════════════════════════════╝
```

**Browser:**
- Beautiful login page loads
- No console errors
- Can login successfully
- Dashboard shows wallet and loans

---

**Need help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue on GitHub!
