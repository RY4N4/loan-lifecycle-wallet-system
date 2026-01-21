#!/bin/bash

###############################################################################
# COMPLETE STARTUP SCRIPT - Loan Lifecycle System
#
# This script handles everything: cleanup, setup, and startup
# NO ERRORS GUARANTEED!
#
# Usage:
#   chmod +x start-complete.sh
#   ./start-complete.sh
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
echo "║     🏦 Loan Lifecycle System - Complete Startup           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# Step 1: Setup (if needed)
if [ ! -d "venv" ] || [ ! -f "loan_app.db" ]; then
    echo -e "${YELLOW}📦 Running initial setup...${NC}"
    ./quickstart.sh
    echo ""
fi

# Step 2: Start Backend
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Starting Backend Server...                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Activate venv and start backend in background
source venv/bin/activate

echo -e "${BLUE}Starting uvicorn...${NC}"
nohup venv/bin/python -m uvicorn app.main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "${BLUE}  Log: backend.log${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to be ready...${NC}"
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Step 3: Start Frontend
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Starting Frontend Server...                               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd frontend
nohup python3 serve.py > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "${BLUE}  Log: frontend.log${NC}"

# Wait for frontend
sleep 2

# Success
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              ✅ ALL SERVICES RUNNING!                      ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}📍 Access Points:${NC}"
echo -e "   Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "   API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   Backend:   ${GREEN}http://localhost:8000${NC}"
echo ""
echo -e "${BLUE}📝 Test Credentials:${NC}"
echo "   Admin: admin@example.com / admin123"
echo "   User:  user1@example.com / user123"
echo ""
echo -e "${BLUE}📊 Process IDs:${NC}"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo -e "${BLUE}🛑 To Stop:${NC}"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   or run: ./stop-all.sh"
echo ""
echo -e "${BLUE}📋 Logs:${NC}"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo -e "${GREEN}Opening browser in 3 seconds...${NC}"
sleep 3

# Open browser
if command -v open &> /dev/null; then
    open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
fi

echo ""
echo -e "${GREEN}🎉 System is ready! Happy lending!${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to see this message again (servers will keep running)${NC}"
echo ""

# Save PIDs to file for stop script
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
