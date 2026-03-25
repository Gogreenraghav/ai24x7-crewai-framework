#!/bin/bash
set -e

# CrewAI Framework - One-command startup script

echo "🚀 Starting CrewAI Multi-Agent Framework"
echo "========================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cat > .env << EOF
# GitHub Integration
GITHUB_TOKEN=your_github_token_here

# API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Flask Configuration
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=development

# Redis (optional - will use in-memory if not set)
USE_REDIS=false
REDIS_URL=redis://localhost:6379/0

# Frontend URLs
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_WS_URL=ws://localhost:5000
EOF
    echo "✅ Created .env file. Please edit it with your API keys."
    echo ""
fi

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

if ! command_exists pip3; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
mkdir -p logs
mkdir -p data

# Check if Docker is available for optional services
USE_DOCKER=false
if command_exists docker && command_exists docker-compose; then
    echo "🐳 Docker detected. Do you want to use Docker services (Redis, ChromaDB)? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        USE_DOCKER=true
    fi
fi

if [ "$USE_DOCKER" = true ]; then
    echo "🐳 Starting Docker services..."
    docker-compose up -d redis chromadb
    echo "✅ Docker services started"
    
    # Update environment to use Docker services
    export USE_REDIS=true
    export REDIS_URL=redis://localhost:6379/0
    export CHROMA_HOST=localhost
    export CHROMA_PORT=8000
else
    echo "📝 Running in standalone mode (in-memory queue)"
    export USE_REDIS=false
fi

echo ""

# Run tests (optional)
echo "🧪 Do you want to run tests before starting? (y/n)"
read -r run_tests
if [[ "$run_tests" =~ ^[Yy]$ ]]; then
    echo "Running tests..."
    python -m pytest tests/ -v
    echo ""
fi

# Start the backend server
echo "🎯 Starting CrewAI Backend Server..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backend API:      http://localhost:5000"
echo "API Status:       http://localhost:5000/api/status"
echo "Health Check:     http://localhost:5000/api/health"
echo ""
echo "To submit a project:"
echo "  curl -X POST http://localhost:5000/api/submit-project \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"description\": \"Your project here\"}'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python -m src.api.websocket_server

# Cleanup on exit
trap cleanup EXIT

cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    if [ "$USE_DOCKER" = true ]; then
        echo "Stopping Docker services..."
        docker-compose down
    fi
    deactivate
    echo "✅ Shutdown complete"
}
