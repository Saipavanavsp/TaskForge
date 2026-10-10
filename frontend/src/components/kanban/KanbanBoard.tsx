'use client';

import React, { useState, useMemo } from 'react';
import { Task, TaskPriority, TaskStatus, UserRole } from '@/types';
import TaskCard from './TaskCard';
import TaskModal from './TaskModal';
import { Plus, Search, Filter, Layers, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

interface KanbanBoardProps {
  tasks: Task[];
  projectId: string;
  userRole?: UserRole | null;
  onCreateTask: (data: Partial<Task>) => Promise<void>;
  onUpdateTask: (taskId: string, data: Partial<Task>) => Promise<void>;
  onDeleteTask: (taskId: string) => Promise<void>;
}

const COLUMNS: { id: TaskStatus; title: string; color: string; icon: any }[] = [
  { id: 'todo', title: 'To Do', color: 'border-slate-300 dark:border-slate-700', icon: Layers },
  { id: 'in_progress', title: 'In Progress', color: 'border-blue-400 dark:border-blue-500', icon: Clock },
  { id: 'in_review', title: 'In Review', color: 'border-amber-400 dark:border-amber-500', icon: AlertCircle },
  { id: 'completed', title: 'Completed', color: 'border-emerald-400 dark:border-emerald-500', icon: CheckCircle2 },
];

export default function KanbanBoard({
  tasks,
  projectId,
  userRole,
  onCreateTask,
  onUpdateTask,
  onDeleteTask,
}: KanbanBoardProps) {
  const [search, setSearch] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const canManage = userRole === 'admin' || userRole === 'manager';

  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      const matchesSearch =
        task.title.toLowerCase().includes(search.toLowerCase()) ||
        (task.description && task.description.toLowerCase().includes(search.toLowerCase()));

      const matchesPriority =
        priorityFilter === 'all' || task.priority === priorityFilter;

      return matchesSearch && matchesPriority;
    });
  }, [tasks, search, priorityFilter]);

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleModalSubmit = async (data: Partial<Task>) => {
    if (editingTask) {
      await onUpdateTask(editingTask.id, data);
    } else {
      await onCreateTask(data);
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls & Filter Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 bg-white dark:bg-slate-800/80 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm backdrop-blur-md">
        <div className="flex items-center gap-3 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter tasks by keyword..."
              className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 dark:text-slate-100"
            />
          </div>

          {/* Priority filter pills */}
          <div className="hidden sm:flex items-center gap-1.5 bg-slate-100 dark:bg-slate-900/60 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
            {['all', 'urgent', 'high', 'medium', 'low'].map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-2.5 py-1 text-[11px] font-medium rounded-md capitalize transition ${
                  priorityFilter === p
                    ? 'bg-white dark:bg-slate-800 text-teal-600 dark:text-teal-400 shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          {canManage ? (
            <button
              onClick={() => {
                setEditingTask(null);
                setIsModalOpen(true);
              }}
              className="flex items-center justify-center gap-1.5 px-4 py-2 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition"
            >
              <Plus className="w-4 h-4" />
              <span>New Task</span>
            </button>
          ) : (
            <div className="text-[11px] text-slate-400 px-3 py-1.5 bg-slate-100 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
              Role: Member (Read/Update only)
            </div>
          )}
        </div>
      </div>

      {/* Kanban 4-Column Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 items-start">
        {COLUMNS.map((col) => {
          const colTasks = filteredTasks.filter((t) => t.status === col.id);
          const ColIcon = col.icon;

          return (
            <div
              key={col.id}
              className="bg-slate-100/70 dark:bg-slate-900/40 rounded-xl p-3 border border-slate-200 dark:border-slate-800/80 flex flex-col min-h-[500px]"
            >
              {/* Column Header */}
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <ColIcon className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                  <span className="font-semibold text-sm text-slate-800 dark:text-slate-200">
                    {col.title}
                  </span>
                </div>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                  {colTasks.length}
                </span>
              </div>

              {/* Tasks List */}
              <div className="flex-1 space-y-3">
                {colTasks.length === 0 ? (
                  <div className="h-28 border border-dashed border-slate-300 dark:border-slate-800 rounded-lg flex items-center justify-center text-xs text-slate-400">
                    No tasks in {col.title}
                  </div>
                ) : (
                  colTasks.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      onEdit={canManage ? handleEdit : undefined}
                      onDelete={canManage ? onDeleteTask : undefined}
                      canManage={canManage}
                    />
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Task Create/Edit Modal */}
      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleModalSubmit}
        task={editingTask}
        projectId={projectId}
      />
    </div>
  );
}
