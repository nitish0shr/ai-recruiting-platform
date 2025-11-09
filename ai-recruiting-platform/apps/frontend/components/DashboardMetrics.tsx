'use client';

import { motion } from 'framer-motion';
import { 
  Users, 
  Briefcase, 
  TrendingUp, 
  Clock,
  FileText,
  Mail,
  Calendar
} from 'lucide-react';

export function DashboardMetrics() {
  const metrics = [
    {
      title: 'Total Jobs',
      value: '24',
      change: '+12%',
      changeType: 'positive',
      icon: Briefcase,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Active Candidates',
      value: '156',
      change: '+8%',
      changeType: 'positive',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Pipeline Health',
      value: '85%',
      change: '+5%',
      changeType: 'positive',
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Avg Time to Hire',
      value: '28 days',
      change: '-3 days',
      changeType: 'positive',
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
    {
      title: 'New Applications',
      value: '23',
      change: '+15%',
      changeType: 'positive',
      icon: FileText,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
    },
    {
      title: 'Response Rate',
      value: '68%',
      change: '+12%',
      changeType: 'positive',
      icon: Mail,
      color: 'text-pink-600',
      bgColor: 'bg-pink-100',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
      {metrics.map((metric, index) => {
        const Icon = metric.icon;
        return (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg ${metric.bgColor}`}>
                <Icon className={`w-5 h-5 ${metric.color}`} />
              </div>
              <span
                className={`text-xs font-medium ${
                  metric.changeType === 'positive'
                    ? 'text-green-600'
                    : 'text-red-600'
                }`}
              >
                {metric.change}
              </span>
            </div>
            <div className="metric-value text-2xl font-bold text-gray-900 mb-1">
              {metric.value}
            </div>
            <div className="metric-label text-sm text-gray-600">
              {metric.title}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}