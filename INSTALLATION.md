# Installation Guide

## Quick Install (Recommended)

Use the automated startup script:

```bash
./scripts/start.sh
```

This will automatically:
- Check prerequisites
- Create virtual environment
- Install all dependencies
- Set up configuration
- Start the server

## Manual Installation

### 1. Prerequisites

- Python 3.9 or higher
- pip
- git
- (Optional) Docker & Docker Compose

Verify Python version:
```bash
python3 --version  # Should be 3.9+
```

### 2. Clone Repository

```bash
git clone https://github.com/Gogreenraghav/ai24x7-crewai-framework.git
cd ai24x7-crewai-framework
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Flask & Flask-SocketIO (WebSocket server)
- PyGithub (GitHub integration)
- Redis client (task queue)
- pytest (testing)
- All AI/ML libraries

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required
GITHUB_TOKEN=ghp_your_token_here
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional (has defaults)
SECRET_KEY=random-secret-key
FLASK_ENV=development
USE_REDIS=false
```

### 6. Run Tests (Optional)

```bash
pytest tests/ -v
```

### 7. Start Server

```bash
python -m src.api.websocket_server
```

Or with Gunicorn (production):

```bash
gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
         --workers 4 \
         --bind 0.0.0.0:5000 \
         src.api.websocket_server:app
```

## Validation

After installation, run the validation script:

```bash
python validate_integration.py
```

This checks:
- ✅ All modules can be imported
- ✅ GitHub token is valid
- ✅ WebSocket server starts
- ✅ Error handler works
- ✅ Task queue works
- ✅ All tests are discovered

## Docker Installation

### Option 1: Backend Only

```bash
docker build -t crewai-backend .
docker run -p 5000:5000 --env-file .env crewai-backend
```

### Option 2: Full Stack

```bash
docker-compose up -d
```

This starts:
- Backend (port 5000)
- Frontend (port 3000)
- Redis (port 6379)
- ChromaDB (port 8000)

## Troubleshooting

### Import Errors

If you get "No module named 'xyz'":

```bash
pip install -r requirements.txt --force-reinstall
```

### Permission Errors

On Linux/Mac, you may need to make scripts executable:

```bash
chmod +x scripts/start.sh
chmod +x validate_integration.py
```

### Port Already in Use

If port 5000 is in use:

```bash
# Find process
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
FLASK_RUN_PORT=5001 python -m src.api.websocket_server
```

### GitHub Token Issues

Ensure your token has these permissions:
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows

Generate a new token at:
https://github.com/settings/tokens

### Redis Connection Failed

If Redis fails to connect:

1. Install Redis:
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server
   
   # macOS
   brew install redis
   ```

2. Start Redis:
   ```bash
   redis-server
   ```

3. Or use in-memory mode:
   ```env
   USE_REDIS=false
   ```

## Platform-Specific Notes

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Install Redis (optional)
sudo apt install redis-server
```

### macOS

```bash
# Install Homebrew first: https://brew.sh

# Install dependencies
brew install python git

# Install Redis (optional)
brew install redis
brew services start redis
```

### Windows

1. Install Python from python.org
2. Install Git from git-scm.com
3. Use Command Prompt or PowerShell
4. Activate venv: `venv\Scripts\activate`

## Next Steps

After successful installation:

1. **Read the documentation**:
   - [README.md](README.md) - Project overview
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
   - [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - Technical details

2. **Test the API**:
   ```bash
   curl http://localhost:5000/api/health
   curl http://localhost:5000/api/status
   ```

3. **Submit a test project**:
   ```bash
   curl -X POST http://localhost:5000/api/submit-project \
     -H 'Content-Type: application/json' \
     -d '{"description": "Test project"}'
   ```

4. **View the dashboard**:
   - If using Docker: http://localhost:3000
   - Configure frontend separately if needed

## Support

For issues:
- Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
- Review logs in `logs/crewai.log`
- Open an issue on GitHub
