'use client';

import { motion } from 'framer-motion';
import { 
  Users, 
  FileText, 
  UserCheck, 
  Calendar,
  Award,
  CheckCircle
} from 'lucide-react';
import { useState } from 'react';

interface Candidate {
  id: string;
  name: string;
  email: string;
  role: string;
  score: number;
  avatar: string;
}

interface Stage {
  id: string;
  title: string;
  icon: any;
  candidates: Candidate[];
  color: string;
}

export function PipelineBoard() {
  const [stages] = useState<Stage[]>([
    {
      id: 'new',
      title: 'New Applications',
      icon: FileText,
      color: 'text-blue-600',
      candidates: [
        {
          id: '1',
          name: 'Sarah Johnson',
          email: 'sarah.j@example.com',
          role: 'Senior Frontend Developer',
          score: 92,
          avatar: 'SJ'
        },
        {
          id: '2',
          name: 'Mike Chen',
          email: 'mike.chen@example.com',
          role: 'Full Stack Engineer',
          score: 88,
          avatar: 'MC'
        },
      ],
    },
    {
      id: 'screening',
      title: 'Screening',
      icon: Users,
      color: 'text-yellow-600',
      candidates: [
        {
          id: '3',
          name: 'Emily Davis',
          email: 'emily.d@example.com',
          role: 'Product Manager',
          score: 85,
          avatar: 'ED'
        },
        {
          id: '4',
          name: 'Alex Rodriguez',
          email: 'alex.r@example.com',
          role: 'DevOps Engineer',
          score: 90,
          avatar: 'AR'
        },
        {
          id: '5',
          name: 'Lisa Wang',
          email: 'lisa.wang@example.com',
          role: 'Data Scientist',
          score: 87,
          avatar: 'LW'
        },
      ],
    },
    {
      id: 'shortlist',
      title: 'Shortlisted',
      icon: UserCheck,
      color: 'text-green-600',
      candidates: [
        {
          id: '6',
          name: 'David Kim',
          email: 'david.kim@example.com',
          role: 'Backend Developer',
          score: 94,
          avatar: 'DK'
        },
        {
          id: '7',
          name: 'Rachel Green',
          email: 'rachel.g@example.com',
          role: 'UX Designer',
          score: 91,
          avatar: 'RG'
        },
      ],
    },
    {
      id: 'interview',
      title: 'Interview',
      icon: Calendar,
      color: 'text-purple-600',
      candidates: [
        {
          id: '8',
          name: 'Tom Wilson',
          email: 'tom.wilson@example.com',
          role: 'Senior Backend Engineer',
          score: 89,
          avatar: 'TW'
        },
      ],
    },
    {
      id: 'offer',
      title: 'Offer',
      icon: Award,
      color: 'text-indigo-600',
      candidates: [
        {
          id: '9',
          name: 'Jennifer Lee',
          email: 'jennifer.lee@example.com',
          role: 'Lead Developer',
          score: 96,
          avatar: 'JL'
        },
      ],
    },
    {
      id: 'hired',
      title: 'Hired',
      icon: CheckCircle,
      color: 'text-teal-600',
      candidates: [
        {
          id: '10',
          name: 'Robert Brown',
          email: 'robert.brown@example.com',
          role: 'Principal Engineer',
          score: 98,
          avatar: 'RB'
        },
      ],
    },
  ]);

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 80) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6 border-b">
        <h2 className="text-xl font-semibold text-gray-900">Pipeline Overview</h2>
        <p className="text-sm text-gray-600 mt-1">Track candidates through the recruitment process</p>
      </div>
      
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {stages.map((stage, stageIndex) => {
            const Icon = stage.icon;
            return (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: stageIndex * 0.1 }}
                className="pipeline-stage"
              >
                <div className="pipeline-stage-header">
                  <div className="flex items-center space-x-2">
                    <Icon className={`w-5 h-5 ${stage.color}`} />
                    <h3 className="pipeline-stage-title">{stage.title}</h3>
                  </div>
                  <span className="pipeline-stage-count">{stage.candidates.length}</span>
                </div>
                
                <div className="space-y-2">
                  {stage.candidates.map((candidate, candidateIndex) => (
                    <motion.div
                      key={candidate.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.2, delay: candidateIndex * 0.05 }}
                      className="candidate-card"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="candidate-card-header">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-white text-xs font-semibold">
                            {candidate.avatar}
                          </div>
                          <div>
                            <div className="candidate-name">{candidate.name}</div>
                            <div className="text-xs text-gray-500">{candidate.role}</div>
                          </div>
                        </div>
                        <span className={`candidate-score px-2 py-1 rounded text-xs font-medium ${getScoreColor(candidate.score)}`}>
                          {candidate.score}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600">{candidate.email}</div>
                    </motion.div>
                  ))}
                  
                  {stage.candidates.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <Icon className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No candidates in this stage</p>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}