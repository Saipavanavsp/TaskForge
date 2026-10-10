import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.init_db import init_database
from app.middleware.metrics import PrometheusMiddleware, metrics_endpoint
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.services.redis_service import redis_service

setup_logging()
logger = logging.getLogger("taskforge.main")


# WebSocket connection manager for direct FastAPI real-time streaming
class ConnectionManager:
    def __init__(self):
        self.active_rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = set()
        self.active_rooms[room_id].add(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_rooms:
            self.active_rooms[room_id].discard(websocket)
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict):
        if room_id in self.active_rooms:
            data = json.dumps(message)
            for connection in list(self.active_rooms[room_id]):
                try:
                    await connection.send_text(data)
                except Exception:
                    self.disconnect(room_id, connection)


ws_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing TaskForge backend services...")
    await init_database()
    await redis_service.connect()
    
    # Bridge Redis Pub/Sub events into WebSocket manager
    def on_redis_message(channel: str, message_str: str):
        try:
            msg = json.loads(message_str)
            room_id = channel.replace("project:", "")
            asyncio.create_task(ws_manager.broadcast_to_room(room_id, msg))
        except Exception as e:
            logger.error(f"Error bridging redis message: {e}")

    # Listen to all project pub/sub channels locally
    # (In distributed mode, the Node.js socket server also subscribes to Redis)
    yield
    # Shutdown sequence
    logger.info("Shutting down TaskForge backend...")
    await redis_service.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# 1. Observability: OpenTelemetry
if settings.ENABLE_TELEMETRY:
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("OpenTelemetry FastAPI instrumentation activated.")
    except Exception as e:
        logger.warning(f"OpenTelemetry instrumentation warning: {e}")

# 2. Prometheus Metrics Middleware
if settings.ENABLE_METRICS:
    app.add_middleware(PrometheusMiddleware)
    app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)

# 3. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 4. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Include API v1 Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["System"])
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
        "status": "online"
    }


@app.websocket("/ws/projects/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await ws_manager.connect(project_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process incoming client events
            try:
                payload = json.loads(data)
                # Broadcast to room members
                await ws_manager.broadcast_to_room(project_id, payload)
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(project_id, websocket)
