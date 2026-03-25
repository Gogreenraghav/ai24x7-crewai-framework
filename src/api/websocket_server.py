"""
WebSocket Server for Real-time Dashboard Updates
Flask-SocketIO server for agent status streaming and API endpoints.
"""
import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

logger = logging.getLogger(__name__)


# Global state for agent status tracking
agent_status: Dict[str, Any] = {}
task_history: List[Dict[str, Any]] = []
MAX_HISTORY_SIZE = 100


def create_app(config: Dict[str, Any] = None) -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured Flask app
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # Apply custom config
    if config:
        app.config.update(config)
    
    # Enable CORS for Next.js frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://localhost:3001",
                os.getenv('FRONTEND_URL', 'http://localhost:3000')
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    return app


# Create Flask app and SocketIO instance
app = create_app()
socketio = SocketIO(
    app,
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        os.getenv('FRONTEND_URL', 'http://localhost:3000')
    ],
    async_mode='threading',
    logger=True,
    engineio_logger=True
)


# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    client_id = request.sid
    logger.info(f"Client connected: {client_id}")
    
    # Send current agent status to newly connected client
    emit('initial_status', {
        'agents': agent_status,
        'task_history': task_history[-20:]  # Last 20 tasks
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    client_id = request.sid
    logger.info(f"Client disconnected: {client_id}")


@socketio.on('join_room')
def handle_join_room(data):
    """Allow client to join a specific room for targeted updates."""
    room = data.get('room', 'default')
    join_room(room)
    logger.info(f"Client {request.sid} joined room: {room}")
    emit('joined', {'room': room})


@socketio.on('leave_room')
def handle_leave_room(data):
    """Allow client to leave a room."""
    room = data.get('room', 'default')
    leave_room(room)
    logger.info(f"Client {request.sid} left room: {room}")
    emit('left', {'room': room})


@socketio.on('request_status')
def handle_status_request():
    """Handle explicit status request from client."""
    emit('status_update', {
        'agents': agent_status,
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== REST API Endpoints ====================

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get current system and agent status.
    
    Returns:
        JSON with agent status and system info
    """
    return jsonify({
        'success': True,
        'agents': agent_status,
        'task_history': task_history[-20:],
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/submit-project', methods=['POST'])
def submit_project():
    """
    Submit a new project for the multi-agent system to process.
    
    Expected JSON:
        {
            "description": "Project description",
            "requirements": ["req1", "req2"],
            "priority": "high|medium|low"
        }
    
    Returns:
        JSON with task ID and status
    """
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing project description'
            }), 400
        
        # Create task record
        task = {
            'id': f"task_{len(task_history) + 1}",
            'description': data['description'],
            'requirements': data.get('requirements', []),
            'priority': data.get('priority', 'medium'),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'agents_assigned': []
        }
        
        # Add to history
        task_history.append(task)
        if len(task_history) > MAX_HISTORY_SIZE:
            task_history.pop(0)
        
        # Broadcast new task to all connected clients
        socketio.emit('new_task', task)
        
        logger.info(f"New project submitted: {task['id']}")
        
        return jsonify({
            'success': True,
            'task_id': task['id'],
            'message': 'Project submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting project: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get list of all agents and their current status."""
    return jsonify({
        'success': True,
        'agents': agent_status
    })


@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id: str):
    """Get specific agent details."""
    if agent_id not in agent_status:
        return jsonify({
            'success': False,
            'error': 'Agent not found'
        }), 404
    
    return jsonify({
        'success': True,
        'agent': agent_status[agent_id]
    })


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get task history with optional filtering."""
    status_filter = request.args.get('status')
    limit = int(request.args.get('limit', 20))
    
    tasks = task_history
    if status_filter:
        tasks = [t for t in tasks if t['status'] == status_filter]
    
    return jsonify({
        'success': True,
        'tasks': tasks[-limit:],
        'total': len(tasks)
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== Helper Functions for Agent Integration ====================

def update_agent_status(
    agent_id: str,
    status: str,
    current_task: str = None,
    metadata: Dict[str, Any] = None
):
    """
    Update agent status and broadcast to connected clients.
    
    Args:
        agent_id: Unique agent identifier
        status: Agent status (idle, working, error, etc.)
        current_task: Current task description
        metadata: Additional agent metadata
    """
    global agent_status
    
    agent_status[agent_id] = {
        'id': agent_id,
        'status': status,
        'current_task': current_task,
        'last_update': datetime.utcnow().isoformat(),
        'metadata': metadata or {}
    }
    
    # Broadcast to all connected clients
    socketio.emit('agent_status_update', {
        'agent_id': agent_id,
        'status': agent_status[agent_id]
    })
    
    logger.info(f"Agent {agent_id} status updated: {status}")


def update_task_status(task_id: str, status: str, result: Any = None):
    """
    Update task status and broadcast to connected clients.
    
    Args:
        task_id: Task identifier
        status: New status (pending, in_progress, completed, failed)
        result: Task result or error message
    """
    global task_history
    
    for task in task_history:
        if task['id'] == task_id:
            task['status'] = status
            task['updated_at'] = datetime.utcnow().isoformat()
            if result:
                task['result'] = result
            
            # Broadcast update
            socketio.emit('task_status_update', {
                'task_id': task_id,
                'task': task
            })
            
            logger.info(f"Task {task_id} status updated: {status}")
            break


def emit_agent_log(agent_id: str, level: str, message: str):
    """
    Emit agent log message to dashboard.
    
    Args:
        agent_id: Agent identifier
        level: Log level (info, warning, error)
        message: Log message
    """
    socketio.emit('agent_log', {
        'agent_id': agent_id,
        'level': level,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    })


# ==================== Server Entry Point ====================

def run_server(host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
    """
    Run the WebSocket server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        debug: Enable debug mode
    """
    logger.info(f"Starting WebSocket server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_server(debug=True)
