import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import TaskStatus, TaskPriority
from app.schemas.user import UserOut


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "in_progress",
                "assignee_id": "a3bb189e-8bf9-3888-9912-ace4e6543002"
            }
        }
    )


class TaskCreateSchema(BaseModel):
    project_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.todo
    priority: Optional[TaskPriority] = TaskPriority.medium
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None


class TaskOutSchema(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    assignee_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserOut] = None

    model_config = ConfigDict(from_attributes=True)
