'use client';

import { useState } from 'react';
import { Clock, User, Briefcase, Calendar, Mail } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Activity {
  id: string;
  type: 'application' | 'interview' | 'candidate' | 'job';
  description: string;
  timestamp: string;
  details: Record<string, any>;
}

interface RecentActivityProps {
  activities?: Activity[];
}

export function RecentActivity({ activities }: RecentActivityProps) {
  const [filter, setFilter] = useState<string>('all');

  // Sample activities if none provided
  const sampleActivities: Activity[] = [
    {
      id: '1',
      type: 'application',
      description: 'New application received for Senior Software Engineer',
      timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
      details: {
        candidate_name: 'Alice Johnson',
        job_title: 'Senior Software Engineer',
        fit_score: 0.92,
      },
    },
    {
      id: '2',
      type: 'interview',
      description: 'Interview completed with candidate',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      details: {
        candidate_name: 'Bob Smith',
        job_title: 'Product Manager',
        rating: 4.5,
      },
    },
    {
      id: '3',
      type: 'candidate',
      description: 'New candidate added to database',
      timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
      details: {
        candidate_name: 'Carol Davis',
        skills: ['Python', 'Machine Learning', 'TensorFlow'],
      },
    },
    {
      id: '4',
      type: 'job',
      description: 'New job posting created',
      timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
      details: {
        job_title: 'Data Scientist',
        department: 'Engineering',
        location: 'Remote',
      },
    },
  ];

  const activityData = activities || sampleActivities;

  const filteredActivities = activityData.filter((activity) => {
    if (filter === 'all') return true;
    return activity.type === filter;
  });

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'application':
        return FileText;
      case 'interview':
        return Calendar;
      case 'candidate':
        return User;
      case 'job':
        return Briefcase;
      default:
        return Clock;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'application':
        return 'bg-blue-100 text-blue-800';
      case 'interview':
        return 'bg-purple-100 text-purple-800';
      case 'candidate':
        return 'bg-green-100 text-green-800';
      case 'job':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div>
      {/* Filter Tabs */}
      <div className="flex space-x-2 mb-4">
        {['all', 'application', 'interview', 'candidate', 'job'].map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              filter === type
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {/* Activity List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredActivities.map((activity) => {
          const Icon = getActivityIcon(activity.type);
          const colorClass = getActivityColor(activity.type);

          return (
            <div
              key={activity.id}
              className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className={`p-2 rounded-full ${colorClass}`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">
                  {activity.description}
                </p>
                <div className="mt-1 flex items-center text-xs text-gray-500">
                  <Clock className="w-3 h-3 mr-1" />
                  {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                </div>
                
                {/* Activity Details */}
                <div className="mt-2 text-xs text-gray-600">
                  {activity.type === 'application' && (
                    <>
                      <span className="font-medium">{activity.details.candidate_name}</span>
                      {' • '}
                      <span>FitScore: {(activity.details.fit_score * 100).toFixed(0)}%</span>
                    </>
                  )}
                  {activity.type === 'interview' && (
                    <>
                      <span className="font-medium">{activity.details.candidate_name}</span>
                      {' • '}
                      <span>Rating: {activity.details.rating}/5</span>
                    </>
                  )}
                  {activity.type === 'candidate' && (
                    <>
                      <span className="font-medium">Skills:</span>
                      {' '}
                      <span>{activity.details.skills?.slice(0, 3).join(', ')}</span>
                    </>
                  )}
                  {activity.type === 'job' && (
                    <>
                      <span className="font-medium">{activity.details.job_title}</span>
                      {' • '}
                      <span>{activity.details.department}</span>
                      {' • '}
                      <span>{activity.details.location}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredActivities.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No activities found for the selected filter.</p>
        </div>
      )}
    </div>
  );
}