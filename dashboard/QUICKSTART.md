# 🚀 Quick Start Guide

## 1. Install Dependencies (Already Done ✓)

```bash
npm install
```

## 2. Start the Dashboard

```bash
npm run dev
```

The dashboard will be available at: **http://localhost:3000**

## 3. Start the Backend (Optional - For Testing)

If you want to test with the sample backend:

```bash
# Install Python dependencies
pip install flask flask-socketio flask-cors

# Run the sample backend
python BACKEND_EXAMPLE.py
```

The backend will run on **http://localhost:5000**

## 4. Test Without Backend

The dashboard will show a "Disconnected" status if no backend is running. You can still:
- View the UI structure
- See placeholder states
- Submit the project form (it will just show an error)

## 5. Integration with Your CrewAI System

To integrate with your actual CrewAI agents:

### Backend Requirements

Your Python backend needs to:

1. **Install Socket.IO**:
   ```bash
   pip install flask-socketio
   ```

2. **Create WebSocket events**:
   ```python
   from flask_socketio import SocketIO, emit
   
   socketio = SocketIO(app, cors_allowed_origins="*")
   
   # Send agent updates
   socketio.emit('agent_update', {
       "id": "agent-1",
       "name": "Research Analyst",
       "status": "working",
       "currentTask": "Analyzing data...",
       "progress": 45,
       # ... other fields
   })
   ```

3. **Listen for events**:
   ```python
   @socketio.on('submit_project')
   def handle_project(project):
       # Handle new project
       return {"success": True}
   ```

See `BACKEND_EXAMPLE.py` for a complete implementation.

## 6. Customization

### Change Backend URL

Edit `lib/socket.ts`:
```typescript
const socket = io('http://your-backend-url:port', {
  // config
});
```

### Customize Agents

In your backend, send agent data matching this structure:
```typescript
{
  id: string,
  name: string,
  role: string,
  status: 'idle' | 'working' | 'complete' | 'error',
  currentTask: string,
  progress: number, // 0-100
  emoji: string,
  color: string // hex color
}
```

## 7. Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📊 Dashboard Features

- ✅ Real-time agent status with animated avatars
- ✅ Live task timeline with expand/collapse
- ✅ Metrics panel (tasks, tokens, uptime, agents)
- ✅ Project submission form
- ✅ WebSocket connection status
- ✅ Mobile responsive design
- ✅ Dark theme

## 🎨 Avatar Animation States

- **Idle**: Breathing animation (gentle pulse)
- **Working**: Glowing + bouncing + spinner dots
- **Complete**: Bright glow + checkmark
- **Error**: Red pulse + X mark

## 🔌 WebSocket Events Reference

### Frontend → Backend (Emit)

| Event | Data | Description |
|-------|------|-------------|
| `request_state` | - | Request current state |
| `submit_project` | `Project` | Submit new project |

### Backend → Frontend (Listen)

| Event | Data | Description |
|-------|------|-------------|
| `agents_state` | `Agent[]` | Initial/full agent state |
| `agent_update` | `Agent` | Single agent update |
| `agent_status_change` | `{agentId, status, currentTask}` | Quick status update |
| `task_created` | `Task` | New task created |
| `task_update` | `Task` | Task updated |
| `task_completed` | `Task` | Task finished |
| `metrics_update` | `Metrics` | Metrics updated |

## 🐛 Troubleshooting

**Dashboard shows "Disconnected"**
- Make sure backend is running on port 5000
- Check CORS is enabled on backend
- Verify WebSocket support in your backend

**Agents not updating**
- Check browser console for errors
- Verify event names match exactly
- Ensure data structure matches TypeScript types

**Styling issues**
- Run `npm run dev` to rebuild Tailwind
- Clear browser cache
- Check `tailwind.config.ts` paths

## 📝 Next Steps

1. **Integrate with CrewAI**: Connect your actual agents to send updates
2. **Add Authentication**: Secure your dashboard
3. **Add Persistence**: Store tasks in a database
4. **Custom Metrics**: Add domain-specific tracking
5. **Notifications**: Add alerts for critical events

---

**Need help?** Check `README.md` for detailed documentation!
