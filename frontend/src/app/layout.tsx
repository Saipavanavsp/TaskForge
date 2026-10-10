import type { Metadata } from 'next';
import './globals.css';
import Providers from './providers';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'TaskForge — Enterprise Collaborative Task Management',
  description: 'Production-grade collaborative task management platform across all 7 layers of modern web engineering.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full antialiased bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col">
        <Providers>
          <Navbar />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
