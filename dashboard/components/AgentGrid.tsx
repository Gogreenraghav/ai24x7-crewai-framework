'use client';

import { Agent } from '@/types/agent';
import AgentAvatar from './AgentAvatar';
import { getStatusColor } from '@/lib/utils';

interface AgentGridProps {
  agents: Agent[];
}

export default function AgentGrid({ agents }: AgentGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {agents.map((agent) => (
        <div
          key={agent.id}
          className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          {/* Agent Header */}
          <div className="flex items-start gap-4 mb-4">
            <AgentAvatar
              emoji={agent.emoji}
              status={agent.status}
              color={agent.color}
            />
            <div className="flex-1">
              <h3 className="text-xl font-bold text-white mb-1">
                {agent.name}
              </h3>
              <p className="text-sm text-gray-400 mb-2">{agent.role}</p>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)} animate-pulse`} />
                <span className="text-xs text-gray-300 capitalize">
                  {agent.status}
                </span>
              </div>
            </div>
          </div>

          {/* Current Task Speech Bubble */}
          {agent.currentTask && (
            <div className="relative bg-gray-700 rounded-lg p-4 mb-3">
              {/* Speech bubble arrow */}
              <div className="absolute -top-2 left-8 w-4 h-4 bg-gray-700 transform rotate-45" />
              <p className="text-sm text-gray-200 relative z-10">
                {agent.currentTask}
              </p>
            </div>
          )}

          {/* Progress Bar */}
          {agent.status === 'working' && (
            <div className="space-y-2">
              <div className="flex justify-between text-xs text-gray-400">
                <span>Progress</span>
                <span>{agent.progress}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
                  style={{ width: `${agent.progress}%` }}
                >
                  {/* Animated shimmer effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-30 animate-[shimmer_2s_infinite]" 
                       style={{
                         backgroundSize: '200% 100%',
                         animation: 'shimmer 2s infinite linear'
                       }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Status Badge */}
          <div className="mt-4 flex justify-end">
            <span className={`
              px-3 py-1 rounded-full text-xs font-semibold
              ${agent.status === 'idle' ? 'bg-gray-600 text-gray-200' : ''}
              ${agent.status === 'working' ? 'bg-blue-600 text-blue-100' : ''}
              ${agent.status === 'complete' ? 'bg-green-600 text-green-100' : ''}
              ${agent.status === 'error' ? 'bg-red-600 text-red-100' : ''}
            `}>
              {agent.status === 'idle' && '💤 Idle'}
              {agent.status === 'working' && '⚡ Working'}
              {agent.status === 'complete' && '✓ Complete'}
              {agent.status === 'error' && '⚠ Error'}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
