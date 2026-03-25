# CrewAI Framework - Deployment Guide

Complete guide for deploying the CrewAI multi-agent system on various platforms.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [VPS Deployment](#vps-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Docker Deployment](#docker-deployment)
6. [Production Checklist](#production-checklist)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip
- git
- (Optional) Docker & Docker Compose

### One-Command Startup

```bash
./scripts/start.sh
```

This script will:
- Check prerequisites
- Create virtual environment
- Install dependencies
- Set up environment variables
- Start the backend server

---

## Local Development

### Manual Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd crewai-framework
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required variables:
```env
GITHUB_TOKEN=ghp_your_token_here
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=<random-secret-key>
```

5. **Run tests**
```bash
python -m pytest tests/ -v
```

6. **Start the server**
```bash
python -m src.api.websocket_server
```

The API will be available at `http://localhost:5000`

### Development with Hot Reload

For development with auto-reload:

```bash
FLASK_ENV=development python -m src.api.websocket_server
```

---

## VPS Deployment

### Ubuntu/Debian VPS Setup

1. **Update system**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install dependencies**
```bash
sudo apt install -y python3 python3-pip python3-venv git nginx
```

3. **Clone and setup application**
```bash
cd /opt
sudo git clone <your-repo-url> crewai
cd crewai
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
```

4. **Create systemd service**

Create `/etc/systemd/system/crewai.service`:

```ini
[Unit]
Description=CrewAI Multi-Agent Framework
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/crewai
Environment="PATH=/opt/crewai/venv/bin"
EnvironmentFile=/opt/crewai/.env
ExecStart=/opt/crewai/venv/bin/python -m src.api.websocket_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

5. **Start and enable service**
```bash
sudo systemctl daemon-reload
sudo systemctl start crewai
sudo systemctl enable crewai
sudo systemctl status crewai
```

6. **Configure Nginx reverse proxy**

Create `/etc/nginx/sites-available/crewai`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/crewai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

7. **Set up SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Cloud Platforms

### AWS Deployment

#### Option 1: EC2

1. Launch EC2 instance (Ubuntu 22.04)
2. Configure security groups (ports 22, 80, 443, 5000)
3. Follow VPS deployment steps above

#### Option 2: ECS (Docker)

1. Build and push Docker image to ECR
2. Create ECS task definition
3. Configure service with load balancer

```bash
# Build and push
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t crewai .
docker tag crewai:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/crewai:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/crewai:latest
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/crewai
gcloud run deploy crewai --image gcr.io/PROJECT_ID/crewai --platform managed
```

### DigitalOcean

#### App Platform

1. Connect GitHub repository
2. Configure build settings:
   - Build command: `pip install -r requirements.txt`
   - Run command: `python -m src.api.websocket_server`
3. Add environment variables
4. Deploy

---

## Docker Deployment

### Full Stack with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

Services included:
- **backend**: Python API server (port 5000)
- **frontend**: Next.js dashboard (port 3000)
- **redis**: Task queue (port 6379)
- **chromadb**: Vector database (port 8000)

### Docker Swarm / Kubernetes

For orchestration at scale, see `k8s/` directory for Kubernetes manifests.

---

## Production Checklist

### Security

- [ ] Change `SECRET_KEY` to random secure value
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (UFW/iptables)
- [ ] Set up fail2ban for SSH protection
- [ ] Restrict API access (IP whitelist if needed)
- [ ] Enable rate limiting
- [ ] Regular security updates

### Performance

- [ ] Set up Redis for production queue
- [ ] Configure worker processes (Gunicorn)
- [ ] Enable response compression
- [ ] Set up CDN for static assets
- [ ] Database connection pooling
- [ ] Configure caching headers

### Monitoring

- [ ] Set up logging (see Monitoring section)
- [ ] Configure error tracking (Sentry)
- [ ] Set up uptime monitoring
- [ ] Configure alerts for errors
- [ ] Monitor resource usage (CPU, RAM, disk)
- [ ] Track API response times

### Backup

- [ ] Database backups (if using persistent DB)
- [ ] Redis persistence configuration
- [ ] Application logs backup
- [ ] Environment variables backup
- [ ] Automated backup schedule

---

## Monitoring & Maintenance

### Logging

Logs are stored in `logs/` directory:

```bash
# View application logs
tail -f logs/crewai.log

# View error logs
tail -f logs/error.log

# View with systemd (if using service)
sudo journalctl -u crewai -f
```

### Health Checks

```bash
# API health
curl http://localhost:5000/api/health

# System status
curl http://localhost:5000/api/status

# Agent status
curl http://localhost:5000/api/agents
```

### Performance Monitoring

Use Gunicorn for production:

```bash
# Install Gunicorn
pip install gunicorn gevent-websocket

# Run with workers
gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
         --workers 4 \
         --bind 0.0.0.0:5000 \
         src.api.websocket_server:app
```

Update systemd service to use Gunicorn:

```ini
ExecStart=/opt/crewai/venv/bin/gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker --workers 4 --bind 0.0.0.0:5000 src.api.websocket_server:app
```

### Error Tracking with Sentry

Add to `requirements.txt`:
```
sentry-sdk[flask]
```

Add to `src/api/websocket_server.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### Database Maintenance

If using persistent storage:

```bash
# Redis backup
redis-cli SAVE

# ChromaDB backup
docker exec crewai-chromadb /bin/bash -c "cd /chroma && tar czf backup.tar.gz chroma/"
```

### Updates and Upgrades

```bash
# Pull latest code
cd /opt/crewai
sudo git pull

# Install new dependencies
sudo venv/bin/pip install -r requirements.txt

# Restart service
sudo systemctl restart crewai
```

### Scaling

For high traffic, consider:

1. **Horizontal scaling**: Multiple backend instances behind load balancer
2. **Redis cluster**: For distributed task queue
3. **Database replication**: Read replicas for ChromaDB
4. **CDN**: For static assets and API caching

---

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port 5000
sudo lsof -i :5000
# Kill process
sudo kill -9 <PID>
```

**Module import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**WebSocket connection fails:**
- Check CORS configuration in `websocket_server.py`
- Verify firewall allows WebSocket connections
- Check Nginx configuration for WebSocket proxying

**GitHub integration errors:**
- Verify `GITHUB_TOKEN` is valid
- Check token permissions (repo, workflow access)
- Ensure rate limits not exceeded

### Support

For issues and questions:
- GitHub Issues: `<your-repo-url>/issues`
- Documentation: `docs/`
- Logs: `logs/crewai.log`

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GITHUB_TOKEN` | GitHub personal access token | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes | - |
| `SECRET_KEY` | Flask secret key | Yes | - |
| `FLASK_ENV` | Flask environment | No | `production` |
| `USE_REDIS` | Enable Redis queue | No | `false` |
| `REDIS_URL` | Redis connection URL | No | `redis://localhost:6379/0` |
| `FRONTEND_URL` | Frontend dashboard URL | No | `http://localhost:3000` |
| `CHROMA_HOST` | ChromaDB host | No | `localhost` |
| `CHROMA_PORT` | ChromaDB port | No | `8000` |

---

**Last updated**: 2025-03-25
