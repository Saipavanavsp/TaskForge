import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.middleware.rbac import verify_jwt_and_role
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreateSchema, TaskOutSchema, TaskUpdateSchema
from app.services.redis_service import redis_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskOutSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreateSchema,
    db: AsyncSession = Depends(get_db),
    auth_payload: dict = Depends(verify_jwt_and_role(["admin", "manager"]))
):
    new_task = Task(
        project_id=task_in.project_id,
        assignee_id=task_in.assignee_id,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status,
        priority=task_in.priority,
        due_date=task_in.due_date
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    # Load relationship for assignee
    query = select(Task).options(selectinload(Task.assignee)).where(Task.id == new_task.id)
    res = await db.execute(query)
    task_full = res.scalar_one()

    # Publish real-time event
    task_data = TaskOutSchema.model_validate(task_full).model_dump(mode="json")
    await redis_service.publish(
        f"project:{task_full.project_id}",
        {"type": "task:created", "task": task_data}
    )

    return task_full


@router.get("/{id}", response_model=TaskOutSchema)
async def get_task(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Task).options(selectinload(Task.assignee)).where(Task.id == id)
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.patch("/{id}", response_model=TaskOutSchema)
async def update_task(
    id: uuid.UUID,
    task_update: TaskUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Task).options(selectinload(Task.assignee)).where(Task.id == id)
    result = await db.execute(query)
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Apply updates
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.assignee_id is not None:
        if task_update.assignee_id == "" or task_update.assignee_id == "unassigned":
            task.assignee_id = None
        else:
            try:
                task.assignee_id = uuid.UUID(task_update.assignee_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid assignee UUID format"
                )

    await db.commit()
    await db.refresh(task)

    # Re-fetch with assignee loaded
    query = select(Task).options(selectinload(Task.assignee)).where(Task.id == task.id)
    res = await db.execute(query)
    task_full = res.scalar_one()

    # Publish real-time event to project channel
    task_data = TaskOutSchema.model_validate(task_full).model_dump(mode="json")
    await redis_service.publish(
        f"project:{task_full.project_id}",
        {"type": "task:updated", "task": task_data}
    )

    return task_full


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    auth_payload: dict = Depends(verify_jwt_and_role(["admin", "manager"]))
):
    result = await db.execute(select(Task).where(Task.id == id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    project_id = task.project_id
    task_id = task.id

    await db.delete(task)
    await db.commit()

    # Broadcast task deletion
    await redis_service.publish(
        f"project:{project_id}",
        {"type": "task:deleted", "task_id": str(task_id)}
    )

    return None
