'use client';

import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useAuthStore } from '@/lib/store/authStore';
import { api } from '@/lib/api';
import { DashboardStats } from '@/components/DashboardStats';
import { RecentActivity } from '@/components/RecentActivity';
import { QuickActions } from '@/components/QuickActions';
import { FitScoreChart } from '@/components/FitScoreChart';
import { ApplicationsPipeline } from '@/components/ApplicationsPipeline';
import { TopCandidates } from '@/components/TopCandidates';

export default function Dashboard() {
  const { user } = useAuthStore();
  
  const { data: analytics, isLoading: analyticsLoading } = useQuery(
    'analytics',
    () => api.get('/api/analytics/dashboard').then(res => res.data),
    {
      enabled: !!user,
    }
  );

  const { data: recentActivity } = useQuery(
    'recent-activity',
    () => api.get('/api/analytics/detailed?days=7').then(res => res.data),
    {
      enabled: !!user,
    }
  );

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Loading Dashboard...</h1>
          <div className="loading-spinner mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user.first_name}!
          </h1>
          <p className="text-gray-600 mt-2">
            Here's what's happening with your recruiting pipeline today.
          </p>
        </div>

        {/* Dashboard Stats */}
        <DashboardStats analytics={analytics} loading={analyticsLoading} />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* FitScore Chart */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">FitScore Distribution</h2>
              <FitScoreChart data={analytics?.fit_score_distribution} />
            </div>

            {/* Applications Pipeline */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Applications Pipeline</h2>
              <ApplicationsPipeline data={analytics?.applications_by_status} />
            </div>

            {/* Recent Activity */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
              <RecentActivity activities={recentActivity?.recent_activity} />
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            {/* Quick Actions */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <QuickActions />
            </div>

            {/* Top Candidates */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Candidates</h2>
              <TopCandidates candidates={analytics?.top_candidates} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}