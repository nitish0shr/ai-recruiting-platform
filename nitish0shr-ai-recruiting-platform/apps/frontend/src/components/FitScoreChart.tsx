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

interface FitScoreChartProps {
  data?: Array<{ score: number; count: number }>;
}

export function FitScoreChart({ data }: FitScoreChartProps) {
  // Sample data if no data provided
  const chartData = data || [
    { score: 0.9, count: 12 },
    { score: 0.8, count: 25 },
    { score: 0.7, count: 18 },
    { score: 0.6, count: 8 },
    { score: 0.5, count: 5 },
  ];

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
            return `Candidates: ${context.parsed.y}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Candidates',
        },
      },
      x: {
        title: {
          display: true,
          text: 'FitScore Range',
        },
      },
    },
  };

  const formattedData = {
    labels: chartData.map((d) => `${(d.score * 100).toFixed(0)}%`),
    datasets: [
      {
        label: 'Candidates',
        data: chartData.map((d) => d.count),
        backgroundColor: [
          '#10b981',
          '#34d399',
          '#6ee7b7',
          '#a7f3d0',
          '#d1fae5',
        ],
        borderColor: '#059669',
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