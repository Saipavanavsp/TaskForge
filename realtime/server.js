const http = require('http');
const { Server } = require('socket.io');
const Redis = require('ioredis');

const PORT = process.env.PORT || 4001;
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379/0';

const server = http.createServer((req, res) => {
  if (req.url === '/health' || req.url === '/healthz/liveness') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', service: 'taskforge-realtime' }));
  } else {
    res.writeHead(404);
    res.end();
  }
});

const io = new Server(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

// Setup Redis subscriber with resilient fallback
let redisSub = null;
try {
  redisSub = new Redis(REDIS_URL, {
    maxRetriesPerRequest: 1,
    retryStrategy: () => 5000 // Retry every 5s if disconnected
  });

  redisSub.on('connect', () => {
    console.log('[Realtime] Connected to Redis pub/sub broker');
    redisSub.psubscribe('project:*', (err, count) => {
      if (err) console.error('[Realtime] psubscribe error:', err);
      else console.log(`[Realtime] Subscribed to pattern project:*, count: ${count}`);
    });
  });

  redisSub.on('pmessage', (pattern, channel, message) => {
    try {
      const data = JSON.parse(message);
      const projectId = channel.replace('project:', '');
      // Broadcast to room
      io.to(projectId).emit(data.type || 'task:event', data);
      console.log(`[Realtime] Broadcasted ${data.type} to room ${projectId}`);
    } catch (e) {
      console.error('[Realtime] Error parsing Redis pub/sub message:', e);
    }
  });

  redisSub.on('error', (err) => {
    // Suppress spam if redis is not running locally
    if (err.code === 'ECONNREFUSED') {
      // expected in local dev without docker
    } else {
      console.warn('[Realtime] Redis warning:', err.message);
    }
  });
} catch (e) {
  console.warn('[Realtime] Redis initialization skipped:', e.message);
}

// Track presence
const projectPresence = new Map(); // projectId -> Set of users

io.on('connection', (socket) => {
  console.log(`[Realtime] Client connected: ${socket.id}`);

  socket.on('join:project', ({ projectId, user }) => {
    if (!projectId) return;
    socket.join(projectId);
    socket.data.projectId = projectId;
    socket.data.user = user;

    if (!projectPresence.has(projectId)) {
      projectPresence.set(projectId, new Map());
    }
    if (user && user.id) {
      projectPresence.get(projectId).set(socket.id, user);
    }

    const currentUsers = Array.from(projectPresence.get(projectId).values());
    io.to(projectId).emit('presence:update', {
      projectId,
      users: currentUsers
    });

    console.log(`[Realtime] Socket ${socket.id} joined project ${projectId}`);
  });

  socket.on('leave:project', ({ projectId }) => {
    if (!projectId) return;
    socket.leave(projectId);
    if (projectPresence.has(projectId)) {
      projectPresence.get(projectId).delete(socket.id);
      const currentUsers = Array.from(projectPresence.get(projectId).values());
      io.to(projectId).emit('presence:update', {
        projectId,
        users: currentUsers
      });
    }
  });

  // Client-broadcasted optimistic task drag & drop
  socket.on('task:optimistic_move', (data) => {
    if (data.projectId) {
      socket.to(data.projectId).emit('task:optimistic_move', data);
    }
  });

  socket.on('disconnect', () => {
    const projectId = socket.data.projectId;
    if (projectId && projectPresence.has(projectId)) {
      projectPresence.get(projectId).delete(socket.id);
      const currentUsers = Array.from(projectPresence.get(projectId).values());
      io.to(projectId).emit('presence:update', {
        projectId,
        users: currentUsers
      });
    }
    console.log(`[Realtime] Client disconnected: ${socket.id}`);
  });
});

server.listen(PORT, () => {
  console.log(`[Realtime] TaskForge Socket Server listening on port ${PORT}`);
});
