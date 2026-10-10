'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import Link from 'next/link';
import { Layers, ArrowRight, ShieldCheck, Zap, Database, RefreshCw } from 'lucide-react';

export default function HomePage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isLoading, isAuthenticated, router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[75vh] text-center max-w-4xl mx-auto px-4">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/20 text-xs font-semibold uppercase tracking-wider mb-6">
        <Zap className="w-3.5 h-3.5" /> 7 Layers of Modern Web Engineering
      </div>

      <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-tight">
        Enterprise-Grade Collaborative Task Platform
      </h1>

      <p className="mt-4 text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl leading-relaxed">
        Featuring PostgreSQL 16 with SQLAlchemy 2.0, JWT Access/Refresh token rotation, Argon2id encryption, RBAC middleware, TanStack Query optimistic updates, and real-time distributed sync.
      </p>

      <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
        <Link
          href="/login"
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-semibold text-sm shadow-lg shadow-teal-600/25 transition transform active:scale-95"
        >
          <span>Launch Dashboard</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
        <Link
          href="/register"
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-900 dark:text-slate-100 font-semibold text-sm transition"
        >
          <span>Create Enterprise Account</span>
        </Link>
      </div>

      {/* Feature Badges */}
      <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-left">
          <Database className="w-5 h-5 text-teal-500 mb-2" />
          <div className="text-xs font-bold text-slate-800 dark:text-slate-200">PostgreSQL 16</div>
          <div className="text-[11px] text-slate-500 mt-1">SQLAlchemy 2.0 & Alembic</div>
        </div>
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-left">
          <ShieldCheck className="w-5 h-5 text-purple-500 mb-2" />
          <div className="text-xs font-bold text-slate-800 dark:text-slate-200">Argon2id + JWT</div>
          <div className="text-[11px] text-slate-500 mt-1">HttpOnly Cookie Rotation</div>
        </div>
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-left">
          <RefreshCw className="w-5 h-5 text-blue-500 mb-2" />
          <div className="text-xs font-bold text-slate-800 dark:text-slate-200">Optimistic UI</div>
          <div className="text-[11px] text-slate-500 mt-1">TanStack Query v5 Rollback</div>
        </div>
        <div className="p-4 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-left">
          <Zap className="w-5 h-5 text-amber-500 mb-2" />
          <div className="text-xs font-bold text-slate-800 dark:text-slate-200">Real-time Engine</div>
          <div className="text-[11px] text-slate-500 mt-1">Redis Pub/Sub & Socket.io</div>
        </div>
      </div>
    </div>
  );
}
