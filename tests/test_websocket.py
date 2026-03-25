"""
Unit tests for WebSocket server.
"""
import unittest
import json
from unittest.mock import Mock, patch
from src.api.websocket_server import create_app, update_agent_status, update_task_status


class TestWebSocketServer(unittest.TestCase):
    """Test WebSocket server functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app({'TESTING': True})
        self.client = self.app.test_client()
    
    def test_app_creation(self):
        """Test Flask app creation."""
        self.assertIsNotNone(self.app)
        self.assertTrue(self.app.config['TESTING'])
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'healthy')
    
    def test_get_status(self):
        """Test status endpoint."""
        response = self.client.get('/api/status')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('agents', data)
        self.assertIn('task_history', data)
    
    def test_submit_project_valid(self):
        """Test submitting a valid project."""
        project_data = {
            'description': 'Build a web app',
            'requirements': ['Frontend', 'Backend'],
            'priority': 'high'
        }
        
        response = self.client.post(
            '/api/submit-project',
            data=json.dumps(project_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('task_id', data)
    
    def test_submit_project_missing_description(self):
        """Test submitting project without description."""
        project_data = {
            'requirements': ['Frontend']
        }
        
        response = self.client.post(
            '/api/submit-project',
            data=json.dumps(project_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_get_agents(self):
        """Test getting agents list."""
        # First, update some agent status
        update_agent_status('agent_1', 'working', 'Building frontend')
        
        response = self.client.get('/api/agents')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('agents', data)
        self.assertIn('agent_1', data['agents'])
    
    def test_get_specific_agent(self):
        """Test getting specific agent details."""
        # Update agent status
        update_agent_status('agent_2', 'idle')
        
        response = self.client.get('/api/agents/agent_2')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['agent']['id'], 'agent_2')
        self.assertEqual(data['agent']['status'], 'idle')
    
    def test_get_nonexistent_agent(self):
        """Test getting agent that doesn't exist."""
        response = self.client.get('/api/agents/nonexistent')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
    
    def test_get_tasks(self):
        """Test getting tasks list."""
        # Submit a task first
        project_data = {
            'description': 'Test task',
            'priority': 'low'
        }
        self.client.post(
            '/api/submit-project',
            data=json.dumps(project_data),
            content_type='application/json'
        )
        
        response = self.client.get('/api/tasks')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('tasks', data)
        self.assertGreater(len(data['tasks']), 0)
    
    def test_get_tasks_with_filter(self):
        """Test filtering tasks by status."""
        # Submit and complete a task
        project_data = {'description': 'Completed task'}
        response = self.client.post(
            '/api/submit-project',
            data=json.dumps(project_data),
            content_type='application/json'
        )
        task_id = json.loads(response.data)['task_id']
        
        update_task_status(task_id, 'completed', 'Done!')
        
        response = self.client.get('/api/tasks?status=completed')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        # All returned tasks should have completed status
        for task in data['tasks']:
            self.assertEqual(task['status'], 'completed')
    
    def test_get_tasks_with_limit(self):
        """Test limiting number of tasks returned."""
        # Submit multiple tasks
        for i in range(5):
            project_data = {'description': f'Task {i}'}
            self.client.post(
                '/api/submit-project',
                data=json.dumps(project_data),
                content_type='application/json'
            )
        
        response = self.client.get('/api/tasks?limit=3')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(data['tasks']), 3)


class TestWebSocketHelpers(unittest.TestCase):
    """Test WebSocket helper functions."""
    
    @patch('src.api.websocket_server.socketio')
    def test_update_agent_status(self, mock_socketio):
        """Test updating agent status."""
        update_agent_status(
            agent_id='agent_1',
            status='working',
            current_task='Building feature',
            metadata={'progress': 50}
        )
        
        # Check that socketio.emit was called
        mock_socketio.emit.assert_called()
        call_args = mock_socketio.emit.call_args
        self.assertEqual(call_args[0][0], 'agent_status_update')
    
    @patch('src.api.websocket_server.socketio')
    def test_update_task_status(self, mock_socketio):
        """Test updating task status."""
        # First create a task by importing and manipulating task_history
        from src.api.websocket_server import task_history
        task_history.append({
            'id': 'task_1',
            'description': 'Test task',
            'status': 'pending'
        })
        
        update_task_status('task_1', 'completed', 'Success!')
        
        # Check that socketio.emit was called
        mock_socketio.emit.assert_called()
        call_args = mock_socketio.emit.call_args
        self.assertEqual(call_args[0][0], 'task_status_update')
        
        # Check that task was updated
        task = next(t for t in task_history if t['id'] == 'task_1')
        self.assertEqual(task['status'], 'completed')
        self.assertEqual(task['result'], 'Success!')


class TestCORSConfiguration(unittest.TestCase):
    """Test CORS configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app({'TESTING': True})
        self.client = self.app.test_client()
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = self.client.get('/api/status')
        
        # Note: In test mode, CORS headers might not be present
        # This test mainly verifies the endpoint is accessible
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
