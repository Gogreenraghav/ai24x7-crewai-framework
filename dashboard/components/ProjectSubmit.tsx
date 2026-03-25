'use client';

import { useState } from 'react';
import { Project } from '@/types/agent';
import { Send, Plus, X } from 'lucide-react';

interface ProjectSubmitProps {
  onSubmit: (project: Project) => void;
}

export default function ProjectSubmit({ onSubmit }: ProjectSubmitProps) {
  const [description, setDescription] = useState('');
  const [requirements, setRequirements] = useState<string[]>(['']);
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addRequirement = () => {
    setRequirements([...requirements, '']);
  };

  const removeRequirement = (index: number) => {
    setRequirements(requirements.filter((_, i) => i !== index));
  };

  const updateRequirement = (index: number, value: string) => {
    const newReqs = [...requirements];
    newReqs[index] = value;
    setRequirements(newReqs);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!description.trim()) {
      alert('Please enter a project description');
      return;
    }

    const filteredRequirements = requirements.filter(req => req.trim() !== '');
    
    if (filteredRequirements.length === 0) {
      alert('Please add at least one requirement');
      return;
    }

    setIsSubmitting(true);

    try {
      const project: Project = {
        description: description.trim(),
        requirements: filteredRequirements,
        priority,
      };

      await onSubmit(project);

      // Reset form
      setDescription('');
      setRequirements(['']);
      setPriority('medium');
    } catch (error) {
      console.error('Error submitting project:', error);
      alert('Failed to submit project. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
        <Send className="w-6 h-6" />
        Submit New Project
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Project Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
            Project Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the project you want the AI crew to work on..."
            className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={4}
            disabled={isSubmitting}
          />
        </div>

        {/* Requirements */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-300">
              Requirements
            </label>
            <button
              type="button"
              onClick={addRequirement}
              className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
              disabled={isSubmitting}
            >
              <Plus className="w-4 h-4" />
              Add Requirement
            </button>
          </div>

          <div className="space-y-3">
            {requirements.map((req, index) => (
              <div key={index} className="flex gap-2">
                <input
                  type="text"
                  value={req}
                  onChange={(e) => updateRequirement(index, e.target.value)}
                  placeholder={`Requirement ${index + 1}`}
                  className="flex-1 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={isSubmitting}
                />
                {requirements.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeRequirement(index)}
                    className="p-2 text-red-400 hover:text-red-300 hover:bg-red-900/20 rounded-lg transition-colors"
                    disabled={isSubmitting}
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Priority
          </label>
          <div className="flex gap-3">
            {(['low', 'medium', 'high'] as const).map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPriority(p)}
                disabled={isSubmitting}
                className={`
                  flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-all
                  ${priority === p
                    ? p === 'low' ? 'bg-green-600 text-white'
                    : p === 'medium' ? 'bg-yellow-600 text-white'
                    : 'bg-red-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }
                `}
              >
                {p.charAt(0).toUpperCase() + p.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
        >
          {isSubmitting ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Submitting...
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              Submit Project
            </>
          )}
        </button>
      </form>
    </div>
  );
}
