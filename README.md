# CrewAI Multi-Agent Framework

A production-ready multi-agent system with GitHub integration, real-time dashboard, error handling, and deployment tooling.

## 🚀 Features

- **Multi-Agent Collaboration**: Coordinate multiple AI agents working together
- **GitHub Integration**: Auto-push agent outputs with proper attribution and conflict handling
- **Real-time Dashboard**: WebSocket-powered dashboard with live agent status updates
- **Error Recovery**: Graceful error handling, retry logic, and auto-restart for crashed agents
- **Task Queue**: Priority-based task queue (Redis or in-memory)
- **Production Ready**: Docker support, systemd services, comprehensive deployment guides

## 📋 Quick Start

### Prerequisites

- Python 3.9+
- pip
- (Optional) Docker & Docker Compose

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd crewai-framework
```

2. **Run the startup script**
```bash
./scripts/start.sh
```

That's it! The script will handle everything else.

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run tests
pytest tests/ -v

# Start server
python -m src.api.websocket_server
```

## 🏗️ Architecture

```
crewai-framework/
├── src/
│   ├── agents/          # Agent implementations
│   ├── api/             # WebSocket server & REST API
│   ├── core/            # Core functionality
│   │   ├── error_handler.py    # Error recovery & retry logic
│   │   └── task_queue.py       # Priority task queue
│   ├── integrations/    # External integrations
│   │   └── github_integration.py  # GitHub auto-push
│   ├── llm/             # LLM providers
│   └── memory/          # Agent memory systems
├── tests/               # Unit tests
├── scripts/             # Utility scripts
├── config/              # Configuration files
├── docker-compose.yml   # Docker orchestration
└── DEPLOYMENT.md        # Deployment guide
```

## 📡 API Endpoints

### REST API

- `GET /api/health` - Health check
- `GET /api/status` - System and agent status
- `POST /api/submit-project` - Submit new project
- `GET /api/agents` - List all agents
- `GET /api/agents/<id>` - Get agent details
- `GET /api/tasks` - Get task history

### WebSocket Events

- `agent_status_update` - Real-time agent status
- `task_status_update` - Task progress updates
- `agent_log` - Agent log messages
- `new_task` - New task created

## 🔧 Configuration

Edit `.env` file with your settings:

```env
# GitHub Integration
GITHUB_TOKEN=ghp_your_token_here

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Flask
SECRET_KEY=random-secret-key
FLASK_ENV=development

# Redis (optional)
USE_REDIS=false
REDIS_URL=redis://localhost:6379/0
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🐳 Docker Deployment

Start all services with Docker Compose:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

Services:
- **backend**: Python API (port 5000)
- **frontend**: Next.js dashboard (port 3000)
- **redis**: Task queue (port 6379)
- **chromadb**: Vector database (port 8000)

## 📦 GitHub Integration

The GitHub integration automatically pushes agent outputs to your repository:

```python
from src.integrations.github_integration import GitHubIntegration

# Initialize
github = GitHubIntegration()
github.set_repository("owner/repo")

# Push file with agent attribution
result = github.push_file(
    file_path="output/result.md",
    content="Agent output...",
    commit_message="Generated output",
    agent_name="Agent-1"
)

# Create PR
pr = github.create_pull_request(
    title="New feature",
    body="Description",
    head_branch="feature",
    agent_name="Agent-2"
)
```

## 🔄 Task Queue

Priority-based task queue with retry logic:

```python
from src.core.task_queue import create_task_queue, Task, TaskPriority

# Create queue (auto-detects Redis or uses in-memory)
queue = create_task_queue()

# Enqueue task
task = Task(
    id="task_1",
    type="build_feature",
    data={"feature": "user_auth"},
    priority=TaskPriority.HIGH
)
queue.enqueue(task)

# Dequeue and process
task = queue.dequeue()
# ... process task ...
queue.complete_task(task.id, result="Done!")
```

## 🛡️ Error Handling

Automatic retry with exponential backoff:

```python
from src.core.error_handler import with_retry, RetryStrategy

@with_retry(
    strategy=RetryStrategy(max_attempts=5, initial_delay=1.0),
    agent_id="agent_1"
)
def unreliable_api_call():
    # Your code here
    pass
```

Safe execution with fallback:

```python
from src.core.error_handler import safe_execute

result = safe_execute(
    risky_function,
    fallback_value="default",
    agent_id="agent_1"
)
```

## 📊 Agent Health Monitoring

Track agent health and auto-restart crashed agents:

```python
from src.core.error_handler import error_handler

# Check agent health
health = error_handler.get_agent_health("agent_1")

# Determine if restart needed
if error_handler.should_restart_agent("agent_1"):
    restart_agent("agent_1")

# Get error summary
summary = error_handler.get_error_summary(agent_id="agent_1")
```

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment guides:

- Local development
- VPS deployment (Ubuntu/Debian)
- Cloud platforms (AWS, GCP, DigitalOcean)
- Docker orchestration
- Production checklist
- Monitoring & maintenance

Quick VPS deployment:

```bash
# On your server
git clone <your-repo-url> /opt/crewai
cd /opt/crewai
./scripts/start.sh
```

## 📝 Example Usage

Submit a project via API:

```bash
curl -X POST http://localhost:5000/api/submit-project \
  -H 'Content-Type: application/json' \
  -d '{
    "description": "Build a web app with user authentication",
    "requirements": ["Frontend", "Backend", "Database"],
    "priority": "high"
  }'
```

Check agent status:

```bash
curl http://localhost:5000/api/agents
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- [Documentation](docs/)
- [API Reference](docs/api.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Issues](issues/)

## 💡 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the documentation
- Review logs in `logs/crewai.log`

---

**Built with ❤️ by the CrewAI Team**
