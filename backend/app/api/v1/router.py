from fastapi import APIRouter
from app.api.v1.endpoints import auth, projects, tasks, health

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(health.router)
