# CrewAI Multi-Agent Dashboard

A beautiful, production-ready Next.js 14 dashboard for real-time monitoring of CrewAI multi-agent systems.

## 🚀 Features

- **Real-time Agent Monitoring**: Track 6 agents with live status updates via WebSocket
- **Animated 2D Avatars**: Canvas-based avatars with state-specific animations:
  - 🧘 Idle state: Breathing animation
  - ⚡ Working state: Typing/thinking animation with spinner
  - ✅ Complete state: Checkmark burst
  - ⚠️ Error state: Red pulse
- **Task Timeline**: Chronological view of all tasks with expand/collapse details
- **Project Submission**: Form to submit new projects with requirements and priority
- **Metrics Dashboard**: Real-time tracking of:
  - Tasks completed
  - Tokens used
  - System uptime
  - Active agents
- **Speech Bubbles**: Live updates showing what each agent is doing
- **Dark Theme**: Modern, eye-friendly UI with Tailwind CSS
- **Mobile Responsive**: Works beautifully on all devices
- **Color-coded Status**: Visual indicators for agent states

## 📦 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Real-time**: Socket.IO Client
- **Animations**: Framer Motion + Canvas API
- **Icons**: Lucide React

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🔌 Backend Integration

The dashboard connects to a Python backend on **port 5000** via WebSocket.

### Expected Backend Events

**Incoming (from backend):**

```javascript
// Initial state
socket.on('agents_state', (agents: Agent[]) => {})
socket.on('metrics_update', (metrics: Metrics) => {})

// Real-time updates
socket.on('agent_update', (agent: Agent) => {})
socket.on('agent_status_change', (data: { agentId, status, currentTask }) => {})
socket.on('task_created', (task: Task) => {})
socket.on('task_update', (task: Task) => {})
socket.on('task_completed', (task: Task) => {})
```

**Outgoing (to backend):**

```javascript
// Request current state
socket.emit('request_state')

// Submit new project
socket.emit('submit_project', project, (response) => {})
```

### Data Types

```typescript
interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'working' | 'complete' | 'error';
  currentTask: string;
  progress: number; // 0-100
  emoji: string;
  color: string; // hex color
}

interface Task {
  id: string;
  agentId: string;
  agentName: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  startTime: string; // ISO timestamp
  endTime?: string;
  result?: string;
}

interface Metrics {
  tasksCompleted: number;
  tokensUsed: number;
  uptime: number; // seconds
  activeAgents: number;
}

interface Project {
  description: string;
  requirements: string[];
  priority: 'low' | 'medium' | 'high';
}
```

## 🎨 Component Structure

```
dashboard/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main dashboard page
│   └── globals.css         # Global styles
├── components/
│   ├── AgentAvatar.tsx     # Animated 2D avatar
│   ├── AgentGrid.tsx       # 6-agent grid display
│   ├── TaskTimeline.tsx    # Expandable task history
│   ├── MetricsPanel.tsx    # 4 metric cards
│   └── ProjectSubmit.tsx   # Project submission form
├── lib/
│   ├── socket.ts           # WebSocket client
│   └── utils.ts            # Helper functions
└── types/
    └── agent.ts            # TypeScript interfaces
```

## 🎯 Usage

1. **Start the backend** on port 5000 with Socket.IO support
2. **Run the dashboard**: `npm run dev`
3. **Open browser**: http://localhost:3000
4. **Submit projects** and watch agents work in real-time!

## 🔧 Configuration

To change the backend URL, edit `lib/socket.ts`:

```typescript
const socket = io('http://localhost:5000', {
  // your config
});
```

## 📱 Responsive Design

- **Desktop**: Full 3-column agent grid, side-by-side layouts
- **Tablet**: 2-column grid, stacked panels
- **Mobile**: Single column, optimized for touch

## 🎭 Avatar Animations

Each agent avatar is rendered on a Canvas element with state-specific animations:

- **Idle**: Gentle breathing (scale + opacity pulse)
- **Working**: Glowing aura + bouncing emoji + spinner dots
- **Complete**: Bright glow + checkmark overlay
- **Error**: Red pulse + X mark overlay

## 🚦 Status Colors

- 🟢 Complete: Green
- 🔵 Working: Blue
- ⚪ Idle: Gray
- 🔴 Error: Red

## 📝 License

MIT

## 🤝 Contributing

This is a production-ready template. Feel free to customize and extend!

---

Built with ❤️ for CrewAI multi-agent systems
