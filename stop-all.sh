#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Stopping Jīva Health services...${NC}"

# Kill processes by PID if files exist
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✅ Backend stopped${NC}" || echo -e "${YELLOW}⚠️  Backend not running${NC}"
    rm -f .backend.pid
fi

if [ -f ".expo.pid" ]; then
    EXPO_PID=$(cat .expo.pid)
    kill $EXPO_PID 2>/dev/null && echo -e "${GREEN}✅ Expo stopped${NC}" || echo -e "${YELLOW}⚠️  Expo not running${NC}"
    rm -f .expo.pid
fi

# Kill by port as backup
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:19006 | xargs kill -9 2>/dev/null
lsof -ti:19000 | xargs kill -9 2>/dev/null

echo -e "${GREEN}✅ All services stopped${NC}"
