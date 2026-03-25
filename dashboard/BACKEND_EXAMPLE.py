"""
Sample Python backend for CrewAI Dashboard
This is an example implementation showing how to integrate with the frontend.
"""

from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Sample agent data
agents = [
    {
        "id": "agent-1",
        "name": "Research Analyst",
        "role": "Data Research & Analysis",
        "status": "idle",
        "currentTask": "",
        "progress": 0,
        "emoji": "🔍",
        "color": "#3b82f6"
    },
    {
        "id": "agent-2",
        "name": "Content Writer",
        "role": "Content Creation",
        "status": "idle",
        "currentTask": "",
        "progress": 0,
        "emoji": "✍️",
        "color": "#8b5cf6"
    },
    {
        "id": "agent-3",
        "name": "Code Developer",
        "role": "Software Development",
        "status": "idle",
        "currentTask": "",
        "progress": 0,
        "emoji": "💻",
        "color": "#10b981"
    },
    {
        "id": "agent-4",
        "name": "QA Tester",
        "role": "Quality Assurance",
        "status": "idle",
        "currentTask": "",
        "progress": 0,
        "emoji": "🧪",
        "color": "#f59e0b"
    },
    {
        "id": "agent-5",
        "name": "Designer",
        "role": "UI/UX Design",
        "status": "idle",
        "currentTask": "",
        "progress": 0,
        "emoji": "🎨",
        "color": "#ec4899"
    },
    {
        "id": "agent-6",
        "name": "Project Manager",
        "role": "Coordination & Planning",
        "status": "idle",
        "currentTask": "",
        "progress": 0,
        "emoji": "📋",
        "color": "#6366f1"
    }
]

tasks = []
metrics = {
    "tasksCompleted": 0,
    "tokensUsed": 0,
    "uptime": 0,
    "activeAgents": 0
}

start_time = time.time()

@socketio.on('connect')
def handle_connect():
    print('✅ Client connected')
    emit('agents_state', agents)
    emit('metrics_update', metrics)

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')

@socketio.on('request_state')
def handle_request_state():
    """Send current state to client"""
    emit('agents_state', agents)
    emit('metrics_update', metrics)
    for task in tasks:
        emit('task_update', task)

@socketio.on('submit_project')
def handle_submit_project(project):
    """Handle new project submission"""
    print(f"📋 New project received: {project['description']}")
    
    # Create tasks for the project
    for i, requirement in enumerate(project['requirements']):
        agent = agents[i % len(agents)]
        task = {
            "id": f"task-{int(time.time())}-{i}",
            "agentId": agent['id'],
            "agentName": agent['name'],
            "description": requirement,
            "status": "pending",
            "startTime": datetime.now().isoformat(),
        }
        tasks.append(task)
        emit('task_created', task, broadcast=True)
    
    # Start working on first task (demo)
    if tasks:
        task = tasks[-len(project['requirements'])]
        task['status'] = 'in-progress'
        agent = next(a for a in agents if a['id'] == task['agentId'])
        agent['status'] = 'working'
        agent['currentTask'] = task['description']
        agent['progress'] = 10
        
        emit('task_update', task, broadcast=True)
        emit('agent_update', agent, broadcast=True)
    
    return {"success": True}

@socketio.on('update_agent_progress')
def handle_update_progress(data):
    """Update agent progress (called by your CrewAI agents)"""
    agent_id = data['agentId']
    progress = data['progress']
    
    agent = next((a for a in agents if a['id'] == agent_id), None)
    if agent:
        agent['progress'] = progress
        emit('agent_update', agent, broadcast=True)

@socketio.on('complete_task')
def handle_complete_task(data):
    """Mark task as complete"""
    task_id = data['taskId']
    result = data.get('result', '')
    
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        task['status'] = 'completed'
        task['endTime'] = datetime.now().isoformat()
        task['result'] = result
        
        # Update agent status
        agent = next((a for a in agents if a['id'] == task['agentId']), None)
        if agent:
            agent['status'] = 'complete'
            agent['progress'] = 100
            emit('agent_update', agent, broadcast=True)
        
        # Update metrics
        metrics['tasksCompleted'] += 1
        metrics['tokensUsed'] += random.randint(100, 1000)
        
        emit('task_completed', task, broadcast=True)
        emit('metrics_update', metrics, broadcast=True)

def update_metrics():
    """Background task to update metrics"""
    while True:
        socketio.sleep(5)
        metrics['uptime'] = int(time.time() - start_time)
        metrics['activeAgents'] = sum(1 for a in agents if a['status'] != 'idle')
        socketio.emit('metrics_update', metrics, broadcast=True)

if __name__ == '__main__':
    print("🚀 Starting CrewAI Dashboard Backend")
    print("📡 WebSocket server running on http://localhost:5000")
    
    # Start metrics updater in background
    socketio.start_background_task(update_metrics)
    
    # Run server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
