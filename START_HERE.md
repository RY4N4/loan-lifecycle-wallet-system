# 🚀 START HERE - Complete Setup & Run Guide

## ⚡ Super Quick Start (Recommended)

**Run everything with ONE command:**

```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend
./start-complete.sh
```

This will:
- ✅ Setup if needed (first time only)
- ✅ Start backend server
- ✅ Start frontend server
- ✅ Open browser automatically

**That's it!** The system will be running at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

### Test Credentials
- **Admin**: `admin@example.com` / `admin123`
- **User**: `user1@example.com` / `user123`

### Stop All Services
```bash
./stop-all.sh
```

---

## 📖 Manual Start (If You Prefer)

### Terminal 1 - Backend
```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd /Users/cliveleealves/Desktop/SE/loan-lifecycle-backend/frontend
python3 serve.py
```

Then open: http://localhost:3000

---

## 🆘 If Something Goes Wrong

### Problem: Port Already in Use

```bash
# Kill processes on ports
./stop-all.sh

# Or manually:
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Problem: Need Fresh Setup

```bash
# Clean everything and start fresh
./quickstart.sh
```

### Problem: Module Not Found Errors

```bash
# Ensure you're using the venv Python
source venv/bin/activate
which python  # Should show: ./venv/bin/python
```

### Problem: Database Issues

```bash
# Delete and recreate
rm -f loan_app.db
python seed_data.py
```

---

## 📁 What You Have

```
loan-lifecycle-backend/
├── start-complete.sh     ⭐ ONE-COMMAND START (USE THIS!)
├── stop-all.sh          🛑 Stop all services
├── quickstart.sh        📦 Fresh setup script
├── EASY_SETUP.md        📖 Detailed setup guide
├── GITHUB_SETUP.md      🐙 GitHub instructions
├── app/                 💻 Backend code
├── frontend/            🎨 Web interface
└── *.md                 📚 Documentation
```

---

## ✅ Success Checklist

When everything is working, you should have:

- [ ] Backend log shows: "Application startup complete"
- [ ] Can access http://localhost:8000/docs (API docs)
- [ ] Frontend loads at http://localhost:3000
- [ ] Can login with test credentials
- [ ] EMI calculator works when applying for loan
- [ ] No console errors in browser

---

## 🎯 What to Do Next

### Test the System
1. **Register** new user → Check wallet created
2. **Apply for loan** → See real-time EMI calculation
3. **Login as admin** → Approve the loan
4. **Back to user** → Check wallet credited
5. **Make payment** → Verify deduction
6. **View transactions** → See complete history

### Put on GitHub
```bash
# See complete instructions in:
cat GITHUB_SETUP.md
```

### Customize
- **Change colors**: Edit `frontend/styles.css`
- **Add features**: Check `CONTRIBUTING.md`
- **Deploy**: See `DEPLOYMENT.md`

---

## 📚 Full Documentation

- [EASY_SETUP.md](EASY_SETUP.md) - Troubleshooting & detailed setup
- [frontend/README.md](frontend/README.md) - Frontend user guide
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Push to GitHub
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [README_DETAILED.md](README_DETAILED.md) - Complete technical docs

---

## 🎉 That's All!

**Just run:**
```bash
./start-complete.sh
```

**System ready in < 10 seconds!**

Need help? Check [EASY_SETUP.md](EASY_SETUP.md) for troubleshooting.

---

Made with ❤️ for easy deployment
