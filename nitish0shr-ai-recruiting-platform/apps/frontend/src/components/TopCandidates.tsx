'use client';

import { useRouter } from 'next/navigation';
import { Star, MapPin, Briefcase, TrendingUp } from 'lucide-react';

interface Candidate {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  current_title?: string;
  current_company?: string;
  location?: string;
  fit_score: number;
  skills: string[];
}

interface TopCandidatesProps {
  candidates?: Candidate[];
}

export function TopCandidates({ candidates }: TopCandidatesProps) {
  const router = useRouter();

  // Sample candidates if none provided
  const sampleCandidates: Candidate[] = [
    {
      id: '1',
      first_name: 'Alice',
      last_name: 'Johnson',
      email: 'alice.johnson@email.com',
      current_title: 'Senior Developer',
      current_company: 'TechStart Inc',
      location: 'San Francisco, CA',
      fit_score: 0.95,
      skills: ['Python', 'React', 'AWS', 'Docker'],
    },
    {
      id: '2',
      first_name: 'Bob',
      last_name: 'Smith',
      email: 'bob.smith@email.com',
      current_title: 'Software Architect',
      current_company: 'Enterprise Corp',
      location: 'New York, NY',
      fit_score: 0.92,
      skills: ['Java', 'Spring', 'Microservices', 'Kubernetes'],
    },
    {
      id: '3',
      first_name: 'Carol',
      last_name: 'Davis',
      email: 'carol.davis@email.com',
      current_title: 'Product Manager',
      current_company: 'ProductCo',
      location: 'Seattle, WA',
      fit_score: 0.89,
      skills: ['Product Strategy', 'Agile', 'Analytics'],
    },
    {
      id: '4',
      first_name: 'David',
      last_name: 'Wilson',
      email: 'david.wilson@email.com',
      current_title: 'Data Scientist',
      current_company: 'DataTech',
      location: 'Remote',
      fit_score: 0.87,
      skills: ['Machine Learning', 'Python', 'TensorFlow'],
    },
  ];

  const candidateData = candidates || sampleCandidates;

  const getFitScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-100';
    if (score >= 0.8) return 'text-blue-600 bg-blue-100';
    if (score >= 0.7) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className="space-y-4">
      {candidateData.slice(0, 5).map((candidate) => (
        <div
          key={candidate.id}
          className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all cursor-pointer"
          onClick={() => router.push(`/candidates/${candidate.id}`)}
        >
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900">
                {candidate.first_name} {candidate.last_name}
              </h3>
              <p className="text-sm text-gray-600">
                {candidate.current_title || 'Professional'}
              </p>
            </div>
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getFitScoreColor(candidate.fit_score)}`}>
              {(candidate.fit_score * 100).toFixed(0)}%
            </div>
          </div>

          {candidate.current_company && (
            <div className="flex items-center text-sm text-gray-600 mb-1">
              <Briefcase className="w-3 h-3 mr-1" />
              {candidate.current_company}
            </div>
          )}

          {candidate.location && (
            <div className="flex items-center text-sm text-gray-600 mb-2">
              <MapPin className="w-3 h-3 mr-1" />
              {candidate.location}
            </div>
          )}

          <div className="flex flex-wrap gap-1">
            {candidate.skills.slice(0, 3).map((skill) => (
              <span
                key={skill}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
              >
                {skill}
              </span>
            ))}
            {candidate.skills.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                +{candidate.skills.length - 3}
              </span>
            )}
          </div>
        </div>
      ))}

      {candidateData.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No top candidates found.</p>
        </div>
      )}

      <button
        onClick={() => router.push('/candidates')}
        className="w-full mt-4 text-center text-primary-600 hover:text-primary-700 font-medium text-sm"
      >
        View All Candidates →
      </button>
    </div>
  );
}