export type AgentStatus = 'idle' | 'working' | 'complete' | 'error';

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  currentTask: string;
  progress: number;
  emoji: string;
  color: string;
}

export interface Task {
  id: string;
  agentId: string;
  agentName: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  startTime: string;
  endTime?: string;
  result?: string;
}

export interface Metrics {
  tasksCompleted: number;
  tokensUsed: number;
  uptime: number;
  activeAgents: number;
}

export interface Project {
  description: string;
  requirements: string[];
  priority: 'low' | 'medium' | 'high';
}
