'use client';

import { Metrics } from '@/types/agent';
import { formatDuration, formatNumber } from '@/lib/utils';
import { Activity, Zap, Clock, Users } from 'lucide-react';

interface MetricsPanelProps {
  metrics: Metrics;
}

export default function MetricsPanel({ metrics }: MetricsPanelProps) {
  const metricCards = [
    {
      label: 'Tasks Completed',
      value: metrics.tasksCompleted,
      icon: Activity,
      color: 'from-green-500 to-emerald-600',
      bgColor: 'bg-green-500/10',
      iconColor: 'text-green-400',
    },
    {
      label: 'Tokens Used',
      value: formatNumber(metrics.tokensUsed),
      icon: Zap,
      color: 'from-yellow-500 to-orange-600',
      bgColor: 'bg-yellow-500/10',
      iconColor: 'text-yellow-400',
    },
    {
      label: 'System Uptime',
      value: formatDuration(metrics.uptime),
      icon: Clock,
      color: 'from-blue-500 to-cyan-600',
      bgColor: 'bg-blue-500/10',
      iconColor: 'text-blue-400',
    },
    {
      label: 'Active Agents',
      value: metrics.activeAgents,
      icon: Users,
      color: 'from-purple-500 to-pink-600',
      bgColor: 'bg-purple-500/10',
      iconColor: 'text-purple-400',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metricCards.map((metric) => {
        const Icon = metric.icon;
        return (
          <div
            key={metric.label}
            className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-all duration-200 group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`${metric.bgColor} p-3 rounded-lg group-hover:scale-110 transition-transform duration-200`}>
                <Icon className={`w-6 h-6 ${metric.iconColor}`} />
              </div>
              <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${metric.color} animate-pulse`} />
            </div>

            <div className="space-y-1">
              <p className="text-sm text-gray-400 font-medium">
                {metric.label}
              </p>
              <p className={`text-3xl font-bold bg-gradient-to-r ${metric.color} bg-clip-text text-transparent`}>
                {metric.value}
              </p>
            </div>

            {/* Decorative gradient bar */}
            <div className={`mt-4 h-1 rounded-full bg-gradient-to-r ${metric.color} opacity-50`} />
          </div>
        );
      })}
    </div>
  );
}
