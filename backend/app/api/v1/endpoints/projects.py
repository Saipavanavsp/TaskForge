import re
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.middleware.rbac import verify_jwt_and_role
from app.models.enums import TaskPriority, TaskStatus
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOut
from app.schemas.task import TaskOutSchema

router = APIRouter(prefix="/projects", tags=["Projects"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


@router.get("", response_model=List[ProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        select(
            Project,
            func.count(Task.id).label("tasks_count")
        )
        .outerjoin(Task, Project.id == Task.project_id)
        .group_by(Project.id)
        .order_by(Project.created_at.desc())
    )
    result = await db.execute(query)
    rows = result.all()
    
    projects_out = []
    for project, count in rows:
        p_dict = {
            "id": project.id,
            "title": project.title,
            "slug": project.slug,
            "description": project.description,
            "owner_id": project.owner_id,
            "created_at": project.created_at,
            "tasks_count": count
        }
        projects_out.append(ProjectOut(**p_dict))
    return projects_out


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    auth_payload: dict = Depends(verify_jwt_and_role(["admin", "manager"]))
):
    owner_id = uuid.UUID(auth_payload.get("sub"))
    slug = project_in.slug or slugify(project_in.title)
    
    # Check if slug exists
    existing = await db.execute(select(Project).where(Project.slug == slug))
    if existing.scalars().first():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    new_project = Project(
        title=project_in.title,
        slug=slug,
        description=project_in.description,
        owner_id=owner_id
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return ProjectOut(
        id=new_project.id,
        title=new_project.title,
        slug=new_project.slug,
        description=new_project.description,
        owner_id=new_project.owner_id,
        created_at=new_project.created_at,
        tasks_count=0
    )


@router.get("/{id}", response_model=ProjectOut)
async def get_project(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Project).where(Project.id == id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Count tasks
    count_res = await db.execute(
        select(func.count(Task.id)).where(Task.project_id == id)
    )
    tasks_count = count_res.scalar() or 0

    return ProjectOut(
        id=project.id,
        title=project.title,
        slug=project.slug,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at,
        tasks_count=tasks_count
    )


@router.get("/{id}/tasks", response_model=List[TaskOutSchema])
async def get_project_tasks(
    id: uuid.UUID,
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = (
        select(Task)
        .options(selectinload(Task.assignee))
        .where(Task.project_id == id)
    )
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority_filter:
        query = query.where(Task.priority == priority_filter)
    if search:
        query = query.where(
            Task.title.ilike(f"%{search}%") | Task.description.ilike(f"%{search}%")
        )
    
    query = query.order_by(Task.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks
