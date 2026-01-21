#!/bin/bash

###############################################################################
# STOP ALL SERVICES
###############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping all services...${NC}"

# Kill by PID files
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✓ Backend stopped (PID: $BACKEND_PID)${NC}" || echo -e "${YELLOW}Backend already stopped${NC}"
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null && echo -e "${GREEN}✓ Frontend stopped (PID: $FRONTEND_PID)${NC}" || echo -e "${YELLOW}Frontend already stopped${NC}"
    rm .frontend.pid
fi

# Fallback: kill by port
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✓ Killed process on port 8000${NC}"
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo -e "${GREEN}✓ Killed process on port 3000${NC}"

echo -e "${GREEN}All services stopped!${NC}"
