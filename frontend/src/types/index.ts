export type UserRole = 'admin' | 'manager' | 'member';
export type TaskStatus = 'todo' | 'in_progress' | 'in_review' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at?: string;
}

export interface Project {
  id: string;
  title: string;
  slug: string;
  description?: string;
  owner_id: string;
  created_at: string;
  tasks_count?: number;
}

export interface Task {
  id: string;
  project_id: string;
  assignee_id?: string | null;
  title: string;
  description?: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string | null;
  created_at?: string;
  updated_at?: string;
  assignee?: User | null;
}
