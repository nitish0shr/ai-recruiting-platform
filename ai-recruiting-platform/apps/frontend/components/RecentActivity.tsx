'use client';

import { motion } from 'framer-motion';
import { 
  UserPlus, 
  FileText, 
  Mail, 
  Calendar,
  CheckCircle,
  UserCheck,
  Clock
} from 'lucide-react';

interface Activity {
  id: string;
  type: 'candidate_added' | 'resume_uploaded' | 'outreach_sent' | 'interview_scheduled' | 'candidate_hired' | 'candidate_shortlisted';
  description: string;
  timestamp: string;
  user: string;
}

export function RecentActivity() {
  const activities: Activity[] = [
    {
      id: '1',
      type: 'candidate_added',
      description: 'Sarah Johnson applied for Senior Frontend Developer',
      timestamp: '2 minutes ago',
      user: 'System'
    },
    {
      id: '2',
      type: 'resume_uploaded',
      description: 'Resume uploaded for Mike Chen - Full Stack Engineer',
      timestamp: '15 minutes ago',
      user: 'Recruiter'
    },
    {
      id: '3',
      type: 'outreach_sent',
      description: 'Initial outreach sent to Emily Davis',
      timestamp: '1 hour ago',
      user: 'John Doe'
    },
    {
      id: '4',
      type: 'interview_scheduled',
      description: 'Interview scheduled with David Kim for tomorrow',
      timestamp: '2 hours ago',
      user: 'Jane Smith'
    },
    {
      id: '5',
      type: 'candidate_shortlisted',
      description: 'Alex Rodriguez moved to Shortlisted stage',
      timestamp: '3 hours ago',
      user: 'Recruiter'
    },
    {
      id: '6',
      type: 'candidate_hired',
      description: 'Jennifer Lee accepted offer for Lead Developer',
      timestamp: '1 day ago',
      user: 'HR Team'
    }
  ];

  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'candidate_added':
        return UserPlus;
      case 'resume_uploaded':
        return FileText;
      case 'outreach_sent':
        return Mail;
      case 'interview_scheduled':
        return Calendar;
      case 'candidate_hired':
        return CheckCircle;
      case 'candidate_shortlisted':
        return UserCheck;
      default:
        return Clock;
    }
  };

  const getActivityColor = (type: Activity['type']) => {
    switch (type) {
      case 'candidate_added':
        return 'text-blue-600 bg-blue-100';
      case 'resume_uploaded':
        return 'text-green-600 bg-green-100';
      case 'outreach_sent':
        return 'text-purple-600 bg-purple-100';
      case 'interview_scheduled':
        return 'text-orange-600 bg-orange-100';
      case 'candidate_hired':
        return 'text-teal-600 bg-teal-100';
      case 'candidate_shortlisted':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6 border-b">
        <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
        <p className="text-sm text-gray-600 mt-1">Latest updates from your recruitment pipeline</p>
      </div>
      
      <div className="p-6">
        <div className="space-y-4">
          {activities.map((activity, index) => {
            const Icon = getActivityIcon(activity.type);
            const colorClasses = getActivityColor(activity.type);
            
            return (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${colorClasses.split(' ')[1]}`}>
                  <Icon className={`w-4 h-4 ${colorClasses.split(' ')[0]}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.description}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <p className="text-xs text-gray-500">{activity.timestamp}</p>
                    <span className="text-xs text-gray-400">•</span>
                    <p className="text-xs text-gray-500">by {activity.user}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
        
        <div className="mt-6 pt-4 border-t">
          <button className="w-full text-center text-sm text-primary hover:text-primary/80 font-medium">
            View all activity
          </button>
        </div>
      </div>
    </div>
  );
}