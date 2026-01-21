#!/bin/bash

###############################################################################
# START FRONTEND - Loan Lifecycle & Wallet System
# 
# This script starts the frontend development server
#
# Usage:
#   ./start-frontend.sh
#
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Loan Lifecycle Frontend - Starting Server          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if backend is running
echo -e "${YELLOW}Checking if backend is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running on http://localhost:8000${NC}"
else
    echo -e "${RED}✗ Backend is not running!${NC}"
    echo -e "${YELLOW}Please start the backend first:${NC}"
    echo -e "  cd $PROJECT_ROOT"
    echo -e "  source venv/bin/activate"
    echo -e "  uvicorn app.main:app --reload --port 8000"
    echo ""
    echo -e "${YELLOW}Do you want to continue anyway? (y/n)${NC}"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}Starting frontend server...${NC}"
echo ""

# Change to frontend directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.7+${NC}"
    exit 1
fi

# Start the server
echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                 Server Information                    ║${NC}"
echo -e "${BLUE}╠═══════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║  Frontend:  ${GREEN}http://localhost:3000${BLUE}                    ║${NC}"
echo -e "${BLUE}║  Backend:   ${GREEN}http://localhost:8000${BLUE}                    ║${NC}"
echo -e "${BLUE}║  API Docs:  ${GREEN}http://localhost:8000/docs${BLUE}               ║${NC}"
echo -e "${BLUE}╠═══════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║  Press Ctrl+C to stop the server                      ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Run the server
python3 serve.py
