'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Briefcase, 
  TrendingUp, 
  Clock, 
  FileText, 
  Mail,
  Calendar,
  BarChart3,
  Settings,
  Plus,
  Upload,
  Search,
  Filter
} from 'lucide-react';
import { DashboardMetrics } from '@/components/DashboardMetrics';
import { PipelineBoard } from '@/components/PipelineBoard';
import { RecentActivity } from '@/components/RecentActivity';
import { JobModal } from '@/components/JobModal';
import { UploadModal } from '@/components/UploadModal';

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showJobModal, setShowJobModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'jobs', label: 'Jobs', icon: Briefcase },
    { id: 'candidates', label: 'Candidates', icon: Users },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">AI Recruiting Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowUploadModal(true)}
                className="btn btn-secondary flex items-center space-x-2"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Resume</span>
              </button>
              <button
                onClick={() => setShowJobModal(true)}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>New Job</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary text-primary-foreground'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'dashboard' && (
            <div className="space-y-8">
              <DashboardMetrics />
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                  <PipelineBoard />
                </div>
                <div>
                  <RecentActivity />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'jobs' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Job Management</h2>
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Search jobs..."
                      className="pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                  <button className="btn btn-secondary flex items-center space-x-2">
                    <Filter className="w-4 h-4" />
                    <span>Filter</span>
                  </button>
                </div>
              </div>
              
              {/* Job List */}
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="p-6">
                  <div className="space-y-4">
                    {[1, 2, 3].map((job) => (
                      <div key={job} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <h3 className="font-semibold text-gray-900">Senior Software Engineer</h3>
                          <p className="text-sm text-gray-600">San Francisco, CA • Full-time</p>
                          <div className="flex items-center space-x-4 mt-2">
                            <span className="badge badge-primary">15 candidates</span>
                            <span className="badge badge-success">Published</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button className="btn btn-secondary">View</button>
                          <button className="btn btn-primary">Edit</button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'candidates' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Candidate Management</h2>
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Search candidates..."
                      className="pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                  <button className="btn btn-secondary flex items-center space-x-2">
                    <Filter className="w-4 h-4" />
                    <span>Filter</span>
                  </button>
                </div>
              </div>
              
              {/* Candidate List */}
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="p-6">
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map((candidate) => (
                      <div key={candidate} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                            <span className="text-white font-semibold">JD</span>
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">John Doe</h3>
                            <p className="text-sm text-gray-600">john.doe@example.com</p>
                            <div className="flex items-center space-x-2 mt-1">
                              <span className="text-xs text-gray-500">Senior Software Engineer</span>
                              <span className="badge badge-success">85</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="badge badge-primary">Shortlisted</span>
                          <button className="btn btn-secondary">View</button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Analytics & Reports</h2>
              
              {/* Analytics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="metric-card">
                  <div className="metric-label">Total Applications</div>
                  <div className="metric-value">1,234</div>
                  <div className="metric-change metric-change-positive">+12% from last month</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Conversion Rate</div>
                  <div className="metric-value">23.5%</div>
                  <div className="metric-change metric-change-positive">+2.1% from last month</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Time to Hire</div>
                  <div className="metric-value">28 days</div>
                  <div className="metric-change metric-change-negative">+3 days from last month</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Quality Score</div>
                  <div className="metric-value">8.7/10</div>
                  <div className="metric-change metric-change-positive">+0.3 from last month</div>
                </div>
              </div>
              
              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold mb-4">Application Trends</h3>
                  <div className="chart-container flex items-center justify-center text-gray-500">
                    Chart visualization will be implemented here
                  </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold mb-4">Pipeline Conversion</h3>
                  <div className="chart-container flex items-center justify-center text-gray-500">
                    Funnel visualization will be implemented here
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                  <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold mb-4">Organization Settings</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Organization Name
                        </label>
                        <input
                          type="text"
                          className="input w-full"
                          placeholder="Acme Corporation"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Domain
                        </label>
                        <input
                          type="text"
                          className="input w-full"
                          placeholder="acme.com"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Time Zone
                        </label>
                        <select className="input w-full">
                          <option>UTC</option>
                          <option>PST</option>
                          <option>EST</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div>
                  <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h3 className="text-lg font-semibold mb-4">Integrations</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">LinkedIn</div>
                          <div className="text-sm text-gray-600">Connected</div>
                        </div>
                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">Google Calendar</div>
                          <div className="text-sm text-gray-600">Not connected</div>
                        </div>
                        <div className="w-3 h-3 bg-gray-300 rounded-full"></div>
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">ATS</div>
                          <div className="text-sm text-gray-600">Connected</div>
                        </div>
                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Modals */}
      <JobModal
        isOpen={showJobModal}
        onClose={() => setShowJobModal(false)}
      />
      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
      />
    </div>
  );
}