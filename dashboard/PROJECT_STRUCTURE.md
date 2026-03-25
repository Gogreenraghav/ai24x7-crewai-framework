# 📁 Project Structure

```
crewai-framework/dashboard/
│
├── 📄 Configuration Files
│   ├── package.json              # Dependencies and scripts
│   ├── tsconfig.json             # TypeScript configuration
│   ├── tailwind.config.ts        # Tailwind CSS config with custom animations
│   ├── postcss.config.mjs        # PostCSS configuration
│   ├── next.config.mjs           # Next.js configuration
│   ├── .eslintrc.json            # ESLint rules
│   └── .gitignore                # Git ignore patterns
│
├── 📱 App Directory (Next.js 14 App Router)
│   ├── layout.tsx                # Root layout with metadata
│   ├── page.tsx                  # Main dashboard page with WebSocket logic
│   └── globals.css               # Global styles, animations, scrollbar
│
├── 🧩 Components
│   ├── AgentAvatar.tsx           # Canvas-based animated 2D avatars
│   ├── AgentGrid.tsx             # 6-agent card grid with status
│   ├── TaskTimeline.tsx          # Expandable chronological task list
│   ├── MetricsPanel.tsx          # 4 metric cards with gradients
│   └── ProjectSubmit.tsx         # Form to submit new projects
│
├── 🔧 Lib (Utilities)
│   ├── socket.ts                 # WebSocket client initialization
│   ├── utils.ts                  # Helper functions (formatDuration, etc.)
│   └── mockData.ts               # Sample data for testing
│
├── 🪝 Hooks
│   └── useWebSocket.ts           # Custom hook for WebSocket state management
│
├── 📘 Types
│   └── agent.ts                  # TypeScript interfaces (Agent, Task, Metrics, Project)
│
├── 🌐 Public
│   └── favicon.ico               # Favicon
│
├── 📚 Documentation
│   ├── README.md                 # Full documentation
│   ├── QUICKSTART.md             # Quick start guide
│   ├── PROJECT_STRUCTURE.md      # This file
│   └── BACKEND_EXAMPLE.py        # Sample Python backend
│
└── 📦 Generated (after npm install)
    ├── node_modules/             # Dependencies
    ├── .next/                    # Next.js build output
    └── package-lock.json         # Lock file

```

## 🎯 Key Files Explained

### Core Application

**`app/page.tsx`** - Main dashboard
- WebSocket connection management
- Real-time state updates
- Layout orchestration
- Event handlers for agents, tasks, metrics

**`app/layout.tsx`** - Root layout
- Metadata (title, description)
- Font configuration (Inter)
- HTML structure

**`app/globals.css`** - Global styles
- Tailwind directives
- Custom animations (breathing, typing, pulse-error)
- Scrollbar styling
- Utility classes

### Components

**`AgentAvatar.tsx`** - Animated avatars
- Canvas-based rendering
- State-specific animations (idle, working, complete, error)
- Dynamic emoji display
- Status overlays (checkmark, X, spinner)

**`AgentGrid.tsx`** - Agent display grid
- 6-agent responsive grid
- Status indicators
- Speech bubble UI for current tasks
- Progress bars with shimmer effect

**`TaskTimeline.tsx`** - Task history
- Chronological task list
- Expand/collapse details
- Status icons (Lucide React)
- Duration calculations
- Result display

**`MetricsPanel.tsx`** - Metrics cards
- 4 metric cards with icons
- Gradient backgrounds
- Animated hover effects
- Formatted values (K, M notation)

**`ProjectSubmit.tsx`** - Project form
- Description textarea
- Dynamic requirements list
- Priority selection (low/medium/high)
- Form validation
- Loading states

### Utilities & Hooks

**`lib/socket.ts`** - WebSocket client
- Socket.IO initialization
- Connection management
- Auto-reconnect logic
- Event logging

**`lib/utils.ts`** - Helper functions
- `formatDuration()` - Convert seconds to human-readable
- `formatNumber()` - Format large numbers (K, M)
- `getStatusColor()` - Map status to color

**`hooks/useWebSocket.ts`** - WebSocket hook
- Centralized WebSocket state
- Event listener management
- Automatic cleanup
- Type-safe state updates

### Type Definitions

**`types/agent.ts`** - TypeScript interfaces
- `Agent` - Agent structure
- `Task` - Task structure
- `Metrics` - Metrics structure
- `Project` - Project submission structure
- `AgentStatus` - Status enum

## 🎨 Styling Approach

- **Tailwind CSS** - Utility-first CSS framework
- **Dark theme** - Gray-900 base with gradient accents
- **Custom animations** - Defined in `tailwind.config.ts`
- **Responsive** - Mobile-first breakpoints
- **Gradients** - Blue/purple theme throughout

## 🔄 Data Flow

```
Backend (Python/Flask)
    ↓ Socket.IO events
WebSocket Client (lib/socket.ts)
    ↓ Event listeners
Main Page (app/page.tsx)
    ↓ State updates
Components (AgentGrid, TaskTimeline, etc.)
    ↓ Render
User Interface
```

## 🚀 Build & Deploy

**Development**:
```bash
npm run dev          # Start dev server (localhost:3000)
```

**Production**:
```bash
npm run build        # Build for production
npm start            # Start production server
```

**Type checking**:
```bash
npx tsc --noEmit     # Check TypeScript errors
```

**Linting**:
```bash
npm run lint         # Run ESLint
```

## 📦 Dependencies

### Core
- `next@14.2.0` - React framework
- `react@18.3.1` - UI library
- `react-dom@18.3.1` - DOM rendering

### Real-time
- `socket.io-client@4.7.0` - WebSocket client

### UI/Animation
- `framer-motion@11.0.0` - Animation library
- `lucide-react@0.344.0` - Icon library
- `tailwindcss@3.4.0` - CSS framework

### Dev
- `typescript@5` - Type checking
- `eslint@8` - Code linting
- `@types/*` - TypeScript definitions

## 🎯 Extension Points

Want to add features? Start here:

- **New metrics**: Add to `MetricsPanel.tsx`
- **Custom agents**: Modify agent data structure in `types/agent.ts`
- **New animations**: Add keyframes to `tailwind.config.ts`
- **Backend events**: Add handlers in `app/page.tsx`
- **New components**: Create in `components/` directory

---

**Everything is production-ready and fully typed!** 🎉
