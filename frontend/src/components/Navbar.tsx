'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import {
  Layers,
  LogOut,
  Moon,
  Sun,
  ShieldCheck,
  UserCheck,
  Users,
  Radio,
  ChevronDown,
} from 'lucide-react';

export default function Navbar() {
  const { user, role, logout, fastSwitchUser } = useAuth();
  const [isDark, setIsDark] = useState(false);
  const [isRoleMenuOpen, setIsRoleMenuOpen] = useState(false);

  const toggleDarkMode = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const getRoleBadge = (r: string | null) => {
    switch (r) {
      case 'admin':
        return 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20';
      case 'manager':
        return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';
      case 'member':
        return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';
      default:
        return 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20';
    }
  };

  return (
    <header className="sticky top-0 z-40 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link href="/dashboard" className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 to-emerald-500 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold text-slate-900 dark:text-white tracking-tight text-base leading-none flex items-center gap-1.5">
              TaskForge
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/20">
                v1.0
              </span>
            </div>
            <div className="text-[10px] text-slate-400 dark:text-slate-500">Collaborative Platform</div>
          </div>
        </Link>

        {/* Realtime Live Pulse */}
        <div className="hidden md:flex items-center space-x-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-600 dark:text-emerald-400 text-xs">
          <Radio className="w-3.5 h-3.5 animate-pulse text-emerald-500" />
          <span className="font-medium text-[11px]">Real-Time Sync Active</span>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-3">
          {/* Quick RBAC Switcher */}
          <div className="relative">
            <button
              onClick={() => setIsRoleMenuOpen(!isRoleMenuOpen)}
              className="flex items-center space-x-1.5 px-2.5 py-1.5 text-xs font-medium rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition"
              title="Quick Switch Role"
            >
              <Users className="w-3.5 h-3.5 text-teal-500" />
              <span className="hidden sm:inline">Role Switcher</span>
              <ChevronDown className="w-3 h-3" />
            </button>

            {isRoleMenuOpen && (
              <div className="absolute right-0 mt-2 w-56 rounded-xl bg-white dark:bg-slate-800 shadow-xl border border-slate-200 dark:border-slate-700 py-1.5 text-xs z-50 animate-in fade-in zoom-in-95">
                <div className="px-3 py-1 text-[10px] font-semibold uppercase text-slate-400 tracking-wider">
                  Fast Demo Switch
                </div>
                <button
                  onClick={() => {
                    fastSwitchUser('dev@taskforge.dev');
                    setIsRoleMenuOpen(false);
                  }}
                  className="w-full px-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 flex items-center justify-between"
                >
                  <div className="flex items-center space-x-2">
                    <ShieldCheck className="w-4 h-4 text-purple-500" />
                    <span className="font-medium text-slate-800 dark:text-slate-200">Dev Admin</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-600">Admin</span>
                </button>

                <button
                  onClick={() => {
                    fastSwitchUser('manager@taskforge.dev');
                    setIsRoleMenuOpen(false);
                  }}
                  className="w-full px-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 flex items-center justify-between"
                >
                  <div className="flex items-center space-x-2">
                    <UserCheck className="w-4 h-4 text-blue-500" />
                    <span className="font-medium text-slate-800 dark:text-slate-200">Sarah Connor</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-600">Manager</span>
                </button>

                <button
                  onClick={() => {
                    fastSwitchUser('member@taskforge.dev');
                    setIsRoleMenuOpen(false);
                  }}
                  className="w-full px-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 flex items-center justify-between"
                >
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4 text-emerald-500" />
                    <span className="font-medium text-slate-800 dark:text-slate-200">Charlie Kent</span>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600">Member</span>
                </button>
              </div>
            )}
          </div>

          {/* Theme Toggle */}
          <button
            onClick={toggleDarkMode}
            className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            title="Toggle Dark Mode"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>

          {/* User Badge & Logout */}
          {user ? (
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-200 dark:border-slate-800">
              <div className="flex items-center space-x-2">
                <div className="w-7 h-7 rounded-full bg-teal-500/20 text-teal-600 dark:text-teal-400 font-bold flex items-center justify-center text-xs">
                  {user.full_name?.charAt(0) || 'U'}
                </div>
                <div className="hidden sm:block">
                  <div className="text-xs font-semibold text-slate-900 dark:text-slate-100 leading-tight">
                    {user.full_name}
                  </div>
                  <div
                    className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.2 rounded border inline-block ${getRoleBadge(
                      role
                    )}`}
                  >
                    {role}
                  </div>
                </div>
              </div>

              <button
                onClick={logout}
                className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/30 transition"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="px-3 py-1.5 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition"
            >
              Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
