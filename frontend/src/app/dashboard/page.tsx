'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/lib/auth-context';
import { apiFetch } from '@/lib/api';
import { Project, Task } from '@/types';
import KanbanBoard from '@/components/kanban/KanbanBoard';
import { useRealtimeProject } from '@/lib/socket';
import {
  FolderPlus,
  Briefcase,
  Layers,
  Sparkles,
  CheckCircle2,
  ListTodo,
  TrendingUp,
} from 'lucide-react';

export default function DashboardPage() {
  const { user, role } = useAuth();
  const queryClient = useQueryClient();
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [isNewProjectModalOpen, setIsNewProjectModalOpen] = useState(false);
  const [newProjectTitle, setNewProjectTitle] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');

  // 1. Fetch Projects
  const { data: projects = [], isLoading: isProjectsLoading } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      return apiFetch<Project[]>('/api/v1/projects');
    },
  });

  // Set default selected project
  const activeProjectId = selectedProjectId || projects[0]?.id;

  // 2. Fetch Tasks for selected project
  const { data: tasks = [], isLoading: isTasksLoading } = useQuery<Task[]>({
    queryKey: ['tasks', activeProjectId],
    queryFn: async () => {
      if (!activeProjectId) return [];
      return apiFetch<Task[]>(`/api/v1/projects/${activeProjectId}/tasks`);
    },
    enabled: !!activeProjectId,
  });

  // Also maintain queryKey: ['tasks'] for the TaskCard mutation cache updates
  const { data: allTasks = tasks } = useQuery<Task[]>({
    queryKey: ['tasks'],
    queryFn: async () => tasks,
    initialData: tasks,
  });

  // 3. Real-time event handling
  useRealtimeProject(activeProjectId, user, (event) => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] });
    queryClient.invalidateQueries({ queryKey: ['tasks', activeProjectId] });
  });

  // 4. Mutations
  const createTaskMutation = useMutation({
    mutationFn: async (newTaskData: Partial<Task>) => {
      return apiFetch<Task>('/api/v1/tasks', {
        method: 'POST',
        body: JSON.stringify(newTaskData),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', activeProjectId] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  const updateTaskMutation = useMutation({
    mutationFn: async ({ taskId, data }: { taskId: string; data: Partial<Task> }) => {
      return apiFetch<Task>(`/api/v1/tasks/${taskId}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', activeProjectId] });
    },
  });

  const deleteTaskMutation = useMutation({
    mutationFn: async (taskId: string) => {
      return apiFetch(`/api/v1/tasks/${taskId}`, {
        method: 'DELETE',
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['tasks', activeProjectId] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  const createProjectMutation = useMutation({
    mutationFn: async ({ title, description }: { title: string; description: string }) => {
      return apiFetch<Project>('/api/v1/projects', {
        method: 'POST',
        body: JSON.stringify({ title, description }),
      });
    },
    onSuccess: (newProj) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setSelectedProjectId(newProj.id);
      setIsNewProjectModalOpen(false);
      setNewProjectTitle('');
      setNewProjectDesc('');
    },
  });

  const currentProject = projects.find((p) => p.id === activeProjectId);
  const canManage = role === 'admin' || role === 'manager';

  // Metrics summary
  const completedCount = tasks.filter((t) => t.status === 'completed').length;
  const inProgressCount = tasks.filter((t) => t.status === 'in_progress').length;
  const urgentCount = tasks.filter((t) => t.priority === 'urgent').length;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          {/* Note: Header must contain 'Project Boards' for Playwright test */}
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Project Boards & Execution
          </h1>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Real-time collaborative task pipeline across distributed services
          </p>
        </div>

        {canManage && (
          <button
            onClick={() => setIsNewProjectModalOpen(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 transition shadow-sm"
          >
            <FolderPlus className="w-4 h-4" />
            <span>New Project</span>
          </button>
        )}
      </div>

      {/* Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700/80 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Total Tasks</div>
            <div className="text-xl font-bold text-slate-900 dark:text-white mt-0.5">{tasks.length}</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center">
            <ListTodo className="w-4 h-4" />
          </div>
        </div>

        <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700/80 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">In Progress</div>
            <div className="text-xl font-bold text-blue-600 dark:text-blue-400 mt-0.5">{inProgressCount}</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center">
            <TrendingUp className="w-4 h-4" />
          </div>
        </div>

        <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700/80 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Completed</div>
            <div className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">{completedCount}</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </div>

        <div className="p-3.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700/80 shadow-sm flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-slate-500 dark:text-slate-400">Urgent Priority</div>
            <div className="text-xl font-bold text-rose-600 dark:text-rose-400 mt-0.5">{urgentCount}</div>
          </div>
          <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400 flex items-center justify-center">
            <Sparkles className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Project Selector Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 overflow-x-auto pb-2">
        {projects.map((p) => {
          const isActive = p.id === activeProjectId;
          return (
            <button
              key={p.id}
              onClick={() => setSelectedProjectId(p.id)}
              className={`flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg whitespace-nowrap transition ${
                isActive
                  ? 'bg-teal-600 text-white shadow-sm'
                  : 'bg-white dark:bg-slate-800/80 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 border border-slate-200 dark:border-slate-700'
              }`}
            >
              <Briefcase className="w-3.5 h-3.5" />
              <span>{p.title}</span>
              {typeof p.tasks_count === 'number' && (
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full ${
                    isActive ? 'bg-teal-700 text-teal-100' : 'bg-slate-100 dark:bg-slate-700 text-slate-500'
                  }`}
                >
                  {p.tasks_count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Kanban Board */}
      {isTasksLoading && tasks.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-xs text-slate-400">
          Loading project tasks...
        </div>
      ) : activeProjectId ? (
        <KanbanBoard
          tasks={tasks}
          projectId={activeProjectId}
          userRole={role}
          onCreateTask={async (data) => {
            await createTaskMutation.mutateAsync({ ...data, project_id: activeProjectId });
          }}
          onUpdateTask={async (taskId, data) => {
            await updateTaskMutation.mutateAsync({ taskId, data });
          }}
          onDeleteTask={async (taskId) => {
            await deleteTaskMutation.mutateAsync(taskId);
          }}
        />
      ) : (
        <div className="p-8 text-center bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-500">No projects found. Please create one to begin.</p>
        </div>
      )}

      {/* Create Project Modal */}
      {isNewProjectModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-slate-800 rounded-xl max-w-md w-full p-6 border border-slate-200 dark:border-slate-700 shadow-2xl">
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-4">
              Create New Project
            </h3>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (newProjectTitle.trim()) {
                  createProjectMutation.mutate({
                    title: newProjectTitle,
                    description: newProjectDesc,
                  });
                }
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Project Title
                </label>
                <input
                  type="text"
                  required
                  value={newProjectTitle}
                  onChange={(e) => setNewProjectTitle(e.target.value)}
                  placeholder="e.g. Distributed Ingestion Engine"
                  className="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 dark:text-slate-100"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                  Description
                </label>
                <textarea
                  rows={3}
                  value={newProjectDesc}
                  onChange={(e) => setNewProjectDesc(e.target.value)}
                  placeholder="High-level milestones and scope..."
                  className="w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 dark:text-slate-100"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200 dark:border-slate-700">
                <button
                  type="button"
                  onClick={() => setIsNewProjectModalOpen(false)}
                  className="px-3.5 py-1.5 text-xs text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createProjectMutation.isPending}
                  className="px-4 py-1.5 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm disabled:opacity-50"
                >
                  {createProjectMutation.isPending ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
