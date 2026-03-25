#!/bin/bash

echo "🔍 CrewAI Dashboard - Verification Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
passed=0
failed=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((passed++))
    else
        echo -e "${RED}✗${NC} $1"
        ((failed++))
    fi
}

# Check files exist
echo "📁 Checking Core Files..."
[ -f "package.json" ] && check "package.json exists" || check "package.json exists"
[ -f "tsconfig.json" ] && check "tsconfig.json exists" || check "tsconfig.json exists"
[ -f "tailwind.config.ts" ] && check "tailwind.config.ts exists" || check "tailwind.config.ts exists"
[ -f "next.config.mjs" ] && check "next.config.mjs exists" || check "next.config.mjs exists"

echo ""
echo "🧩 Checking Components..."
[ -f "components/AgentAvatar.tsx" ] && check "AgentAvatar.tsx exists" || check "AgentAvatar.tsx exists"
[ -f "components/AgentGrid.tsx" ] && check "AgentGrid.tsx exists" || check "AgentGrid.tsx exists"
[ -f "components/TaskTimeline.tsx" ] && check "TaskTimeline.tsx exists" || check "TaskTimeline.tsx exists"
[ -f "components/MetricsPanel.tsx" ] && check "MetricsPanel.tsx exists" || check "MetricsPanel.tsx exists"
[ -f "components/ProjectSubmit.tsx" ] && check "ProjectSubmit.tsx exists" || check "ProjectSubmit.tsx exists"

echo ""
echo "📱 Checking App Files..."
[ -f "app/page.tsx" ] && check "app/page.tsx exists" || check "app/page.tsx exists"
[ -f "app/layout.tsx" ] && check "app/layout.tsx exists" || check "app/layout.tsx exists"
[ -f "app/globals.css" ] && check "app/globals.css exists" || check "app/globals.css exists"

echo ""
echo "🔧 Checking Utilities..."
[ -f "lib/socket.ts" ] && check "lib/socket.ts exists" || check "lib/socket.ts exists"
[ -f "lib/utils.ts" ] && check "lib/utils.ts exists" || check "lib/utils.ts exists"
[ -f "hooks/useWebSocket.ts" ] && check "hooks/useWebSocket.ts exists" || check "hooks/useWebSocket.ts exists"
[ -f "types/agent.ts" ] && check "types/agent.ts exists" || check "types/agent.ts exists"

echo ""
echo "📚 Checking Documentation..."
[ -f "README.md" ] && check "README.md exists" || check "README.md exists"
[ -f "QUICKSTART.md" ] && check "QUICKSTART.md exists" || check "QUICKSTART.md exists"
[ -f "DEPLOYMENT.md" ] && check "DEPLOYMENT.md exists" || check "DEPLOYMENT.md exists"
[ -f "BACKEND_EXAMPLE.py" ] && check "BACKEND_EXAMPLE.py exists" || check "BACKEND_EXAMPLE.py exists"

echo ""
echo "📦 Checking Dependencies..."
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✓${NC} node_modules installed"
    ((passed++))
    
    # Check specific packages
    [ -d "node_modules/next" ] && check "next installed" || check "next installed"
    [ -d "node_modules/react" ] && check "react installed" || check "react installed"
    [ -d "node_modules/socket.io-client" ] && check "socket.io-client installed" || check "socket.io-client installed"
    [ -d "node_modules/tailwindcss" ] && check "tailwindcss installed" || check "tailwindcss installed"
else
    echo -e "${RED}✗${NC} node_modules not installed"
    ((failed++))
fi

echo ""
echo "🔨 Checking Build..."
if [ -d ".next" ]; then
    echo -e "${GREEN}✓${NC} Build directory exists"
    ((passed++))
else
    echo -e "${YELLOW}⚠${NC}  Build not found (run 'npm run build')"
fi

echo ""
echo "=========================================="
echo -e "Results: ${GREEN}${passed} passed${NC}, ${RED}${failed} failed${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Dashboard is ready!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Review above.${NC}"
    exit 1
fi
