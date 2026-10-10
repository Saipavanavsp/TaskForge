'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import React from 'react';
import { Task, TaskPriority } from '@/types';
import { AlertCircle, Calendar, Clock, Edit2, Trash2, User } from 'lucide-react';

interface TaskCardProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
  canManage?: boolean;
}

export default function TaskCard({ task, onEdit, onDelete, canManage }: TaskCardProps) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (newStatus: Task['status']) => {
      const res = await fetch(`/api/v1/tasks/${task.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!res.ok) throw new Error('Failed to update task status');
      return res.json();
    },
    onMutate: async (newStatus) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['tasks'] });

      // Snapshot previous state
      const previousTasks = queryClient.getQueryData<Task[]>(['tasks']);

      // Optimistically update cache
      queryClient.setQueryData<Task[]>(['tasks'], (old) =>
        old?.map((t) => (t.id === task.id ? { ...t, status: newStatus } : t))
      );

      return { previousTasks };
    },
    onError: (err, newStatus, context) => {
      queryClient.setQueryData(['tasks'], context?.previousTasks);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const getPriorityBadge = (priority?: TaskPriority) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20';
      case 'high':
        return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20';
      case 'medium':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';
      default:
        return 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20';
    }
  };

  return (
    <div className="p-4 bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 transition-all hover:shadow-md hover:border-slate-300 dark:hover:border-slate-600 relative group">
      {/* Priority Pill & Controls */}
      <div className="flex items-center justify-between mb-2">
        <span
          className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full border ${getPriorityBadge(
            task.priority
          )}`}
        >
          {task.priority || 'medium'}
        </span>
        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {onEdit && (
            <button
              onClick={() => onEdit(task)}
              className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded"
              title="Edit Task"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
          )}
          {canManage && onDelete && (
            <button
              onClick={() => onDelete(task.id)}
              className="p-1 text-slate-400 hover:text-red-500 rounded"
              title="Delete Task"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      <h4 className="font-semibold text-slate-900 dark:text-slate-100 text-sm leading-snug">
        {task.title}
      </h4>

      {task.description && (
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
          {task.description}
        </p>
      )}

      {/* Footer Info: Assignee, Due Date & Status Dropdown */}
      <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
        <div className="flex items-center space-x-2">
          {task.assignee ? (
            <div
              className="flex items-center space-x-1"
              title={task.assignee.email}
            >
              <div className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-600 dark:text-teal-400 font-bold flex items-center justify-center text-[10px]">
                {task.assignee.full_name.charAt(0)}
              </div>
              <span className="text-[11px] truncate max-w-[80px]">
                {task.assignee.full_name.split(' ')[0]}
              </span>
            </div>
          ) : (
            <div className="flex items-center space-x-1 text-slate-400">
              <User className="w-3.5 h-3.5" />
              <span className="text-[10px]">Unassigned</span>
            </div>
          )}
        </div>

        <select
          value={task.status}
          onChange={(e) => mutation.mutate(e.target.value as Task['status'])}
          className="text-xs p-1 rounded border border-slate-300 dark:bg-slate-900 dark:border-slate-600 dark:text-slate-200 cursor-pointer focus:ring-1 focus:ring-teal-500 outline-none"
        >
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="in_review">In Review</option>
          <option value="completed">Completed</option>
        </select>
      </div>
    </div>
  );
}
