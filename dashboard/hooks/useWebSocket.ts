'use client';

import { useEffect, useState } from 'react';
import { Socket } from 'socket.io-client';
import { getSocket, disconnectSocket } from '@/lib/socket';
import { Agent, Task, Metrics } from '@/types/agent';

interface WebSocketState {
  socket: Socket | null;
  isConnected: boolean;
  agents: Agent[];
  tasks: Task[];
  metrics: Metrics;
}

export const useWebSocket = () => {
  const [state, setState] = useState<WebSocketState>({
    socket: null,
    isConnected: false,
    agents: [],
    tasks: [],
    metrics: {
      tasksCompleted: 0,
      tokensUsed: 0,
      uptime: 0,
      activeAgents: 0,
    },
  });

  useEffect(() => {
    const socket = getSocket();
    setState(prev => ({ ...prev, socket }));

    // Connection handlers
    const handleConnect = () => {
      setState(prev => ({ ...prev, isConnected: true }));
    };

    const handleDisconnect = () => {
      setState(prev => ({ ...prev, isConnected: false }));
    };

    // Agent handlers
    const handleAgentsState = (agents: Agent[]) => {
      setState(prev => ({ ...prev, agents }));
    };

    const handleAgentUpdate = (agent: Agent) => {
      setState(prev => ({
        ...prev,
        agents: prev.agents.map(a => a.id === agent.id ? agent : a),
      }));
    };

    const handleAgentStatusChange = (data: { 
      agentId: string; 
      status: Agent['status']; 
      currentTask?: string 
    }) => {
      setState(prev => ({
        ...prev,
        agents: prev.agents.map(agent =>
          agent.id === data.agentId
            ? { ...agent, status: data.status, currentTask: data.currentTask || agent.currentTask }
            : agent
        ),
      }));
    };

    // Task handlers
    const handleTaskCreated = (task: Task) => {
      setState(prev => ({
        ...prev,
        tasks: [task, ...prev.tasks],
      }));
    };

    const handleTaskUpdate = (task: Task) => {
      setState(prev => ({
        ...prev,
        tasks: prev.tasks.map(t => t.id === task.id ? task : t),
      }));
    };

    const handleTaskCompleted = (task: Task) => {
      setState(prev => ({
        ...prev,
        tasks: prev.tasks.map(t => t.id === task.id ? task : t),
      }));
    };

    // Metrics handler
    const handleMetricsUpdate = (metrics: Metrics) => {
      setState(prev => ({ ...prev, metrics }));
    };

    // Register all listeners
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('agents_state', handleAgentsState);
    socket.on('agent_update', handleAgentUpdate);
    socket.on('agent_status_change', handleAgentStatusChange);
    socket.on('task_created', handleTaskCreated);
    socket.on('task_update', handleTaskUpdate);
    socket.on('task_completed', handleTaskCompleted);
    socket.on('metrics_update', handleMetricsUpdate);

    // Request initial state
    socket.emit('request_state');

    // Cleanup
    return () => {
      socket.off('connect', handleConnect);
      socket.off('disconnect', handleDisconnect);
      socket.off('agents_state', handleAgentsState);
      socket.off('agent_update', handleAgentUpdate);
      socket.off('agent_status_change', handleAgentStatusChange);
      socket.off('task_created', handleTaskCreated);
      socket.off('task_update', handleTaskUpdate);
      socket.off('task_completed', handleTaskCompleted);
      socket.off('metrics_update', handleMetricsUpdate);
      disconnectSocket();
    };
  }, []);

  return state;
};
