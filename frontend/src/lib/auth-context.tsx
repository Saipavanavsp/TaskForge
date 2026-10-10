'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, UserRole } from '@/types';
import { apiFetch, getAuthToken, setAuthToken } from './api';

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  fastSwitchUser: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCurrentUser = async () => {
    try {
      if (getAuthToken()) {
        const u = await apiFetch<User>('/api/v1/auth/me');
        setUser(u);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
      setAuthToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    setIsLoading(true);
    try {
      const data = await apiFetch<{ access_token: string; user: User }>('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      setAuthToken(data.access_token);
      setUser(data.user);
      return data.user;
    } finally {
      setIsLoading(false);
    }
  };

  const fastSwitchUser = async (email: string) => {
    await login(email, 'SecurePassword123!');
  };

  const logout = async () => {
    try {
      await apiFetch('/api/v1/auth/logout', { method: 'POST' });
    } catch {
      // ignore
    } finally {
      setAuthToken(null);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role: user?.role || null,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        fastSwitchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
