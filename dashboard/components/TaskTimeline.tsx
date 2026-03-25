'use client';

import { useState } from 'react';
import { Task } from '@/types/agent';
import { ChevronDown, ChevronUp, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';

interface TaskTimelineProps {
  tasks: Task[];
}

export default function TaskTimeline({ tasks }: TaskTimelineProps) {
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set());

  const toggleTask = (taskId: string) => {
    const newExpanded = new Set(expandedTasks);
    if (newExpanded.has(taskId)) {
      newExpanded.delete(taskId);
    } else {
      newExpanded.add(taskId);
    }
    setExpandedTasks(newExpanded);
  };

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'in-progress':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const formatTime = (timeStr: string) => {
    const date = new Date(timeStr);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const calculateDuration = (start: string, end?: string) => {
    if (!end) return null;
    const duration = new Date(end).getTime() - new Date(start).getTime();
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <Clock className="w-6 h-6" />
        Task Timeline
      </h2>

      {tasks.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No tasks yet. Submit a project to get started!</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
          {tasks.map((task, index) => {
            const isExpanded = expandedTasks.has(task.id);
            const duration = calculateDuration(task.startTime, task.endTime);

            return (
              <div
                key={task.id}
                className="bg-gray-750 rounded-lg border border-gray-600 overflow-hidden transition-all duration-200 hover:border-gray-500"
              >
                {/* Task Header */}
                <button
                  onClick={() => toggleTask(task.id)}
                  className="w-full p-4 flex items-start gap-4 text-left hover:bg-gray-700/50 transition-colors"
                >
                  {/* Timeline connector */}
                  <div className="flex flex-col items-center">
                    {getStatusIcon(task.status)}
                    {index < tasks.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-600 mt-2 flex-1" />
                    )}
                  </div>

                  {/* Task Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h3 className="text-sm font-semibold text-white">
                        {task.agentName}
                      </h3>
                      <span className="text-xs text-gray-400 whitespace-nowrap">
                        {formatTime(task.startTime)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300 line-clamp-2">
                      {task.description}
                    </p>
                    {duration && (
                      <span className="text-xs text-gray-500 mt-1 inline-block">
                        Duration: {duration}
                      </span>
                    )}
                  </div>

                  {/* Expand/Collapse Icon */}
                  <div className="flex-shrink-0 pt-1">
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                </button>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-4 pb-4 border-t border-gray-600 bg-gray-800/50">
                    <div className="pt-4 space-y-3">
                      <div>
                        <span className="text-xs font-semibold text-gray-400 uppercase">
                          Status
                        </span>
                        <div className="mt-1">
                          <span className={`
                            px-2 py-1 rounded text-xs font-medium
                            ${task.status === 'completed' ? 'bg-green-900/50 text-green-200' : ''}
                            ${task.status === 'failed' ? 'bg-red-900/50 text-red-200' : ''}
                            ${task.status === 'in-progress' ? 'bg-blue-900/50 text-blue-200' : ''}
                            ${task.status === 'pending' ? 'bg-gray-700 text-gray-300' : ''}
                          `}>
                            {task.status}
                          </span>
                        </div>
                      </div>

                      <div>
                        <span className="text-xs font-semibold text-gray-400 uppercase">
                          Timeline
                        </span>
                        <div className="mt-1 text-sm text-gray-300 space-y-1">
                          <div>Started: {formatTime(task.startTime)}</div>
                          {task.endTime && (
                            <div>Ended: {formatTime(task.endTime)}</div>
                          )}
                        </div>
                      </div>

                      {task.result && (
                        <div>
                          <span className="text-xs font-semibold text-gray-400 uppercase">
                            Result
                          </span>
                          <div className="mt-1 text-sm text-gray-300 bg-gray-900 rounded p-3 font-mono">
                            {task.result}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
