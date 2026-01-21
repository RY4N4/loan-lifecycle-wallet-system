#!/bin/bash

###############################################################################
# QUICKSTART SCRIPT - Loan Lifecycle & Wallet System
# 
# This script provides a foolproof setup with SQLite (no PostgreSQL needed!)
#
# Usage:
#   chmod +x quickstart.sh
#   ./quickstart.sh
#
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     🏦 Loan Lifecycle & Wallet System                     ║"
echo "║        Quickstart Setup (SQLite Edition)                   ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📋 Pre-flight Checks...${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Step 1: Clean previous installations
echo ""
echo -e "${YELLOW}Step 1/6: Cleaning previous installations...${NC}"
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi
if [ -f "loan_app.db" ]; then
    echo "Removing old SQLite database..."
    rm -f loan_app.db
fi
echo -e "${GREEN}✓ Clean slate ready${NC}"

# Step 2: Create virtual environment
echo ""
echo -e "${YELLOW}Step 2/6: Creating virtual environment...${NC}"
/usr/bin/python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment created${NC}"

# Step 3: Upgrade pip
echo ""
echo -e "${YELLOW}Step 3/6: Upgrading pip...${NC}"
pip install --upgrade pip -q
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Step 4: Install dependencies
echo ""
echo -e "${YELLOW}Step 4/6: Installing dependencies (this may take a minute)...${NC}"
pip install -q \
    fastapi==0.109.0 \
    "uvicorn[standard]==0.27.0" \
    sqlalchemy==2.0.25 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    "python-jose[cryptography]==3.3.0" \
    "passlib[bcrypt]==1.7.4" \
    python-multipart==0.0.6 \
    python-dotenv==1.0.0

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}❌ Dependency installation failed${NC}"
    exit 1
fi

# Step 5: Configure environment
echo ""
echo -e "${YELLOW}Step 5/6: Configuring environment...${NC}"
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./loan_app.db
SECRET_KEY=dev-secret-key-change-in-production-please-use-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
echo -e "${GREEN}✓ Environment configured with SQLite${NC}"

# Step 6: Initialize database
echo ""
echo -e "${YELLOW}Step 6/6: Initializing database with test data...${NC}"
python seed_data.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database initialized with test users${NC}"
else
    echo -e "${RED}❌ Database initialization failed${NC}"
    exit 1
fi

# Success!
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              ✅ Setup Complete!                            ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}📝 Test Credentials:${NC}"
echo "   Admin: admin@example.com / admin123"
echo "   User1: user1@example.com / user123"
echo "   User2: user2@example.com / user123"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo ""
echo -e "${YELLOW}Terminal 1 - Start Backend:${NC}"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo -e "${YELLOW}Terminal 2 - Start Frontend (open new terminal):${NC}"
echo "   cd frontend"
echo "   python3 serve.py"
echo ""
echo -e "${YELLOW}Then open your browser:${NC}"
echo "   Frontend: ${GREEN}http://localhost:3000${NC}"
echo "   API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}💡 Pro Tip:${NC} Backend must be running before frontend!"
echo ""
echo -e "${GREEN}Happy lending! 🎉${NC}"
echo ""
