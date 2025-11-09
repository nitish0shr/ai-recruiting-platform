'use client';

import { useRouter } from 'next/navigation';
import { Plus, Upload, Search, Mail } from 'lucide-react';

export function QuickActions() {
  const router = useRouter();

  const actions = [
    {
      title: 'Create Job',
      description: 'Post a new job opening',
      icon: Plus,
      onClick: () => router.push('/jobs/create'),
      color: 'bg-blue-500 hover:bg-blue-600',
    },
    {
      title: 'Upload Resume',
      description: 'Add candidate to database',
      icon: Upload,
      onClick: () => router.push('/candidates/upload'),
      color: 'bg-green-500 hover:bg-green-600',
    },
    {
      title: 'Search Candidates',
      description: 'Find qualified candidates',
      icon: Search,
      onClick: () => router.push('/candidates/search'),
      color: 'bg-purple-500 hover:bg-purple-600',
    },
    {
      title: 'Launch Campaign',
      description: 'Start outreach campaign',
      icon: Mail,
      onClick: () => router.push('/campaigns/create'),
      color: 'bg-orange-500 hover:bg-orange-600',
    },
  ];

  return (
    <div className="space-y-3">
      {actions.map((action) => {
        const Icon = action.icon;
        return (
          <button
            key={action.title}
            onClick={action.onClick}
            className={`w-full flex items-center p-3 rounded-lg text-white transition-colors ${action.color}`}
          >
            <Icon className="w-5 h-5 mr-3" />
            <div className="text-left flex-1">
              <p className="font-medium">{action.title}</p>
              <p className="text-sm opacity-90">{action.description}</p>
            </div>
          </button>
        );
      })}
    </div>
  );
}