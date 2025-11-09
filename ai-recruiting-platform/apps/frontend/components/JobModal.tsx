'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Upload, FileText } from 'lucide-react';
import { useState } from 'react';

interface JobModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function JobModal({ isOpen, onClose }: JobModalProps) {
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('text');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [location, setLocation] = useState('');
  const [isParsing, setIsParsing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsParsing(true);
    
    // Simulate AI parsing
    setTimeout(() => {
      setIsParsing(false);
      onClose();
      // Reset form
      setJobTitle('');
      setJobDescription('');
      setLocation('');
    }, 2000);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold text-gray-900">Create New Job</h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="p-6">
              {/* Tab Navigation */}
              <div className="flex space-x-1 mb-6">
                <button
                  onClick={() => setActiveTab('text')}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'text'
                      ? 'bg-primary text-primary-foreground'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Text Input</span>
                </button>
                <button
                  onClick={() => setActiveTab('file')}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === 'file'
                      ? 'bg-primary text-primary-foreground'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Upload className="w-4 h-4" />
                  <span>File Upload</span>
                </button>
              </div>

              <form onSubmit={handleSubmit}>
                {activeTab === 'text' ? (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Job Title
                      </label>
                      <input
                        type="text"
                        value={jobTitle}
                        onChange={(e) => setJobTitle(e.target.value)}
                        className="input w-full"
                        placeholder="e.g., Senior Software Engineer"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Location
                      </label>
                      <input
                        type="text"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        className="input w-full"
                        placeholder="e.g., San Francisco, CA"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Job Description
                      </label>
                      <textarea
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        className="textarea w-full h-32"
                        placeholder="Paste your job description here..."
                        required
                      />
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Upload Job Description
                      </label>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
                        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600 mb-2">
                          Drag and drop your job description file here, or click to browse
                        </p>
                        <p className="text-sm text-gray-500">
                          Supports PDF, DOCX files up to 10MB
                        </p>
                        <button
                          type="button"
                          className="mt-4 btn btn-secondary"
                        >
                          Choose File
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-end space-x-3 pt-6 border-t">
                  <button
                    type="button"
                    onClick={onClose}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isParsing}
                    className="btn btn-primary flex items-center space-x-2"
                  >
                    {isParsing ? (
                      <>
                        <div className="loading-spinner w-4 h-4"></div>
                        <span>Parsing with AI...</span>
                      </>
                    ) : (
                      <span>Create Job</span>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}