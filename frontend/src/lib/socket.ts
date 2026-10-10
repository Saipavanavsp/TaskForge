'use client';

import { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { User } from '@/types';

export function useRealtimeProject(
  projectId: string | undefined,
  user: User | null,
  onTaskEvent: (event: { type: string; task?: any; task_id?: string }) => void
) {
  const socketRef = useRef<Socket | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!projectId) return;

    // 1. Try Socket.io on port 4001 (Node.js engine)
    try {
      const socket = io('http://localhost:4001', {
        transports: ['websocket', 'polling'],
        timeout: 2000,
      });
      socketRef.current = socket;

      socket.on('connect', () => {
        socket.emit('join:project', { projectId, user });
      });

      socket.on('task:created', (data) => onTaskEvent(data));
      socket.on('task:updated', (data) => onTaskEvent(data));
      socket.on('task:deleted', (data) => onTaskEvent(data));
    } catch {
      // ignore
    }

    // 2. Connect to FastAPI WebSocket endpoint as parallel/fallback
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.host;
      const wsUrl = `${protocol}//${wsHost}/ws/projects/${projectId}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onTaskEvent(data);
        } catch {
          // ignore
        }
      };
    } catch {
      // ignore
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.emit('leave:project', { projectId });
        socketRef.current.disconnect();
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [projectId, user?.id]);
}
