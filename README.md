# 🏦 Loan Lifecycle & Wallet Backend System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Ready-003B57?logo=sqlite)](https://www.sqlite.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supported-336791?logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A **production-grade fintech lending platform** with a complete web UI, managing loan applications, wallet balances, EMI repayments, and immutable transaction ledgers with ACID guarantees.

![System Demo](docs/demo-preview.png)

## ✨ Features

### 🔐 **Complete Authentication System**
- User registration with automatic wallet creation
- JWT-based secure authentication
- Role-based access control (USER/ADMIN)
- Session persistence

### 💰 **Real-time Wallet Management**
- Instant balance updates
- Transaction history with audit trail
- Color-coded credits (green) and debits (red)
- Immutable ledger for financial compliance

### 📝 **Smart Loan Application**
- Dynamic loan application form
- **Real-time EMI calculator** - instant feedback as you type
- Configurable tenure (6-60 months) and interest rates
- Multi-state loan lifecycle (PENDING → ACTIVE → CLOSED)

### 💳 **Seamless Repayment Processing**
- Flexible payment amounts (partial or full)
- Idempotent payment processing (no duplicates)
- Automatic loan closure on full repayment
- ACID transaction guarantees

### 👨‍💼 **Admin Control Panel**
- View all pending loan applications
- One-click approve/reject workflow
- Automatic fund disbursement on approval
- User activity monitoring

### 🎨 **Modern Web Interface**
- Responsive design (mobile + desktop)
- Real-time UI updates
- Toast notifications
- Loading states and animations
- No framework dependencies (vanilla JS)

## 🚀 Quick Start (5 Minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/loan-lifecycle-backend.git
cd loan-lifecycle-backend

# Run the quickstart script
chmod +x quickstart.sh
./quickstart.sh
```

This will:
✅ Create virtual environment  
✅ Install all dependencies  
✅ Setup SQLite database (no PostgreSQL needed!)  
✅ Load test data  
✅ Configure environment  

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env file (SQLite is pre-configured)

# Initialize database
python seed_data.py
```

### Start the Application

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

**Access the Application:**
- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| User | user1@example.com | user123 |
| User | user2@example.com | user123 |

## 📸 Screenshots

### Dashboard
![Dashboard](docs/screenshot-dashboard.png)

### Loan Application with EMI Calculator
![Apply Loan](docs/screenshot-apply.png)

### Admin Panel
![Admin Panel](docs/screenshot-admin.png)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│                                                         │
│  Frontend (HTML/CSS/JS) ←→ Backend (FastAPI)           │
│  http://localhost:3000      http://localhost:8000      │
└─────────────────────────────────────────────────────────┘
                              │
                              │ SQLAlchemy ORM
                              │
                    ┌─────────▼──────────┐
                    │  Database Layer    │
                    │                    │
                    │  • SQLite (Dev)    │
                    │  • PostgreSQL(Prod)│
                    └────────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI 0.109.0 - Modern async web framework
- SQLAlchemy 2.0.25 - ORM with ACID transactions
- Pydantic 2.5.3 - Data validation
- JWT - Secure authentication
- Uvicorn - ASGI server

**Frontend:**
- Vanilla JavaScript - No framework overhead
- HTML5/CSS3 - Modern responsive design
- Fetch API - RESTful communication

**Database:**
- SQLite - Development (zero setup)
- PostgreSQL - Production (recommended)

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [EASY_SETUP.md](EASY_SETUP.md) | **Troubleshooting & detailed setup guide** |
| [frontend/README.md](frontend/README.md) | Complete frontend usage guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & patterns |
| [API_REFERENCE.md](API_REFERENCE.md) | Complete API documentation |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide |

## 🧪 Testing

### Run API Tests
```bash
source venv/bin/activate
python test_api.py
```

### Manual Testing

1. **Register a new user** → Verify wallet created with ₹0
2. **Apply for loan** → Check EMI calculator updates in real-time
3. **Login as admin** → Approve the loan
4. **Back to user** → Verify wallet credited
5. **Make payment** → Verify balance decreases
6. **Check transactions** → Verify ledger entry created

## 🔒 Security Features

- ✅ JWT token authentication
- ✅ Password hashing (bcrypt)
- ✅ SQL injection prevention (ORM)
- ✅ CORS configuration
- ✅ Idempotent operations
- ✅ ACID transactions
- ✅ Database constraints

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - User login

### Wallet
- `GET /api/wallet/balance` - Get balance
- `GET /api/wallet/transactions` - Transaction history

### Loans
- `POST /api/loans/apply` - Apply for loan
- `GET /api/loans/my-loans` - User's loans
- `POST /api/loans/calculate-emi` - EMI calculation
- `GET /api/loans/admin/pending` - Pending loans (admin)
- `POST /api/loans/admin/approve` - Approve/reject (admin)

### Repayments
- `POST /api/repayments/make-payment` - Make payment

**Full API documentation:** http://localhost:8000/docs

## 🛠️ Configuration

### Environment Variables

```env
# Database (choose one)
DATABASE_URL=sqlite:///./loan_app.db  # Development
# DATABASE_URL=postgresql://user:pass@localhost:5432/loan_db  # Production

# JWT Configuration
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend Configuration

Edit `frontend/app.js` to change backend URL:
```javascript
const API_BASE_URL = 'http://your-backend-url:8000';
```

## 🚢 Deployment

### Using Docker (Coming Soon)

```bash
docker-compose up -d
```

### Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production deployment instructions covering:
- PostgreSQL setup
- Nginx configuration
- SSL/TLS certificates
- Environment variables
- Monitoring & logging

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 🐛 Troubleshooting

### Common Issues

**1. Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**2. Module not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**3. Database connection errors:**
```bash
# Use SQLite for testing (edit .env)
DATABASE_URL=sqlite:///./loan_app.db
```

**See [EASY_SETUP.md](EASY_SETUP.md) for complete troubleshooting guide.**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: RY4N4(https://github.com/RY4N4)
- Email: ryandsouza03@outlook.com

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust ORM
- PostgreSQL for reliable data storage
- All contributors and testers

## 📈 Project Stats

- **Backend**: 33 Python files, ~5,000 lines
- **Frontend**: 7 files (HTML/CSS/JS), ~1,750 lines
- **Documentation**: 8 comprehensive guides, ~5,000 lines
- **Total**: ~12,000 lines of production-ready code

## 🗺️ Roadmap

- [ ] Docker containerization
- [ ] Kubernetes deployment configs
- [ ] Real-time notifications (WebSocket)
- [ ] Email notifications
- [ ] Document upload for KYC
- [ ] Credit score integration
- [ ] Payment gateway integration
- [ ] Mobile app (React Native)
- [ ] Multi-currency support
- [ ] Advanced analytics dashboard

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/loan-lifecycle-backend&type=Date)](https://star-history.com/#YOUR_USERNAME/loan-lifecycle-backend&Date)

---

**Made with ❤️ for the fintech community**
