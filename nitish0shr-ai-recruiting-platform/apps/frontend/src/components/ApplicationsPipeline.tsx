'use client';

import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface ApplicationsPipelineProps {
  data?: Record<string, number>;
}

export function ApplicationsPipeline({ data }: ApplicationsPipelineProps) {
  // Sample data if no data provided
  const pipelineData = data || {
    new: 15,
    screening: 8,
    interview: 12,
    offer: 3,
    hired: 2,
    rejected: 5,
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            return `Applications: ${context.parsed.y}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Applications',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Application Status',
        },
      },
    },
  };

  const statusColors = {
    new: '#3b82f6',
    screening: '#f59e0b',
    interview: '#8b5cf6',
    offer: '#10b981',
    hired: '#059669',
    rejected: '#ef4444',
  };

  const formattedData = {
    labels: Object.keys(pipelineData).map((status) =>
      status.charAt(0).toUpperCase() + status.slice(1)
    ),
    datasets: [
      {
        label: 'Applications',
        data: Object.values(pipelineData),
        backgroundColor: Object.keys(pipelineData).map(
          (status) => statusColors[status as keyof typeof statusColors] || '#6b7280'
        ),
        borderColor: Object.keys(pipelineData).map(
          (status) => statusColors[status as keyof typeof statusColors] || '#6b7280'
        ),
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="h-64">
      <Bar data={formattedData} options={options} />
    </div>
  );
}