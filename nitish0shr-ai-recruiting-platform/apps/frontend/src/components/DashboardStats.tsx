'use client';

import { TrendingUp, TrendingDown, Users, Briefcase, FileText, Calendar } from 'lucide-react';

interface DashboardStatsProps {
  analytics?: {
    total_jobs: number;
    active_jobs: number;
    total_candidates: number;
    total_applications: number;
    average_fit_score: number;
    conversion_rates: Record<string, number>;
  };
  loading?: boolean;
}

export function DashboardStats({ analytics, loading }: DashboardStatsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  const stats = [
    {
      title: 'Active Jobs',
      value: analytics?.active_jobs || 0,
      icon: Briefcase,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      trend: '+12%',
      trendDirection: 'up',
    },
    {
      title: 'Total Candidates',
      value: analytics?.total_candidates || 0,
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      trend: '+8%',
      trendDirection: 'up',
    },
    {
      title: 'Applications',
      value: analytics?.total_applications || 0,
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      trend: '+15%',
      trendDirection: 'up',
    },
    {
      title: 'Avg FitScore',
      value: `${((analytics?.average_fit_score || 0) * 100).toFixed(1)}%`,
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      trend: '+5%',
      trendDirection: 'up',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        const TrendIcon = stat.trendDirection === 'up' ? TrendingUp : TrendingDown;
        
        return (
          <div key={stat.title} className="card hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                <div className="flex items-center mt-2">
                  <TrendIcon className={`w-4 h-4 ${stat.trendDirection === 'up' ? 'text-green-500' : 'text-red-500'}`} />
                  <span className={`text-sm ml-1 ${stat.trendDirection === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {stat.trend}
                  </span>
                  <span className="text-sm text-gray-500 ml-1">vs last month</span>
                </div>
              </div>
              <div className={`p-3 rounded-full ${stat.bgColor}`}>
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}