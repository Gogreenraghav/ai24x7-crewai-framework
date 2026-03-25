'use client';

import { useEffect, useState } from 'react';
import { Agent, Task, Metrics, Project } from '@/types/agent';
import { getSocket } from '@/lib/socket';
import AgentGrid from '@/components/AgentGrid';
import TaskTimeline from '@/components/TaskTimeline';
import MetricsPanel from '@/components/MetricsPanel';
import ProjectSubmit from '@/components/ProjectSubmit';
import { Activity, Wifi, WifiOff } from 'lucide-react';

export default function Dashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [metrics, setMetrics] = useState<Metrics>({
    tasksCompleted: 0,
    tokensUsed: 0,
    uptime: 0,
    activeAgents: 0,
  });
  const [isConnected, setIsConnected] = useState(false);
  const [showProjectForm, setShowProjectForm] = useState(false);

  useEffect(() => {
    const socket = getSocket();

    // Connection status handlers
    socket.on('connect', () => {
      setIsConnected(true);
      console.log('✅ Connected to backend');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('❌ Disconnected from backend');
    });

    // Agent updates
    socket.on('agent_update', (data: Agent) => {
      setAgents((prev) => {
        const index = prev.findIndex((a) => a.id === data.id);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = data;
          return updated;
        }
        return [...prev, data];
      });
    });

    // Batch agent updates
    socket.on('agents_state', (data: Agent[]) => {
      setAgents(data);
    });

    // Task updates
    socket.on('task_update', (data: Task) => {
      setTasks((prev) => {
        const index = prev.findIndex((t) => t.id === data.id);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = data;
          return updated;
        }
        return [data, ...prev];
      });
    });

    // New task created
    socket.on('task_created', (data: Task) => {
      setTasks((prev) => [data, ...prev]);
    });

    // Task completed
    socket.on('task_completed', (data: Task) => {
      setTasks((prev) => {
        const updated = prev.map((t) => t.id === data.id ? data : t);
        return updated;
      });
    });

    // Metrics updates
    socket.on('metrics_update', (data: Metrics) => {
      setMetrics(data);
    });

    // Agent status change
    socket.on('agent_status_change', (data: { agentId: string; status: Agent['status']; currentTask?: string }) => {
      setAgents((prev) =>
        prev.map((agent) =>
          agent.id === data.agentId
            ? { ...agent, status: data.status, currentTask: data.currentTask || agent.currentTask }
            : agent
        )
      );
    });

    // Request initial state
    socket.emit('request_state');

    // Cleanup
    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('agent_update');
      socket.off('agents_state');
      socket.off('task_update');
      socket.off('task_created');
      socket.off('task_completed');
      socket.off('metrics_update');
      socket.off('agent_status_change');
    };
  }, []);

  const handleProjectSubmit = async (project: Project) => {
    const socket = getSocket();
    
    return new Promise<void>((resolve, reject) => {
      socket.emit('submit_project', project, (response: { success: boolean; error?: string }) => {
        if (response.success) {
          setShowProjectForm(false);
          resolve();
        } else {
          reject(new Error(response.error || 'Failed to submit project'));
        }
      });
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
                <Activity className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  CrewAI Dashboard
                </h1>
                <p className="text-sm text-gray-400">
                  Multi-Agent System Monitor
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Connection Status */}
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                isConnected ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
              }`}>
                {isConnected ? (
                  <>
                    <Wifi className="w-4 h-4" />
                    <span className="text-sm font-medium">Connected</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-4 h-4" />
                    <span className="text-sm font-medium">Disconnected</span>
                  </>
                )}
              </div>

              {/* New Project Button */}
              <button
                onClick={() => setShowProjectForm(!showProjectForm)}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center gap-2"
              >
                <Activity className="w-4 h-4" />
                New Project
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Metrics */}
        <MetricsPanel metrics={metrics} />

        {/* Project Submit Form */}
        {showProjectForm && (
          <ProjectSubmit onSubmit={handleProjectSubmit} />
        )}

        {/* Agent Grid */}
        <div>
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Active Agents
          </h2>
          {agents.length === 0 ? (
            <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
              <Activity className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No agents active yet</p>
              <p className="text-gray-500 text-sm mt-2">Waiting for backend connection...</p>
            </div>
          ) : (
            <AgentGrid agents={agents} />
          )}
        </div>

        {/* Task Timeline */}
        <TaskTimeline tasks={tasks} />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800/50 border-t border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-400 text-sm">
            CrewAI Multi-Agent Dashboard • Real-time monitoring powered by WebSocket
          </p>
        </div>
      </footer>
    </div>
  );
}
