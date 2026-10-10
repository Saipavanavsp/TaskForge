import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    slug: str = Field(..., min_length=2, max_length=180)
    description: Optional[str] = None


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=150)
    slug: Optional[str] = Field(None, min_length=2, max_length=180)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    slug: Optional[str] = Field(None, min_length=2, max_length=180)
    description: Optional[str] = None


class ProjectOut(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    tasks_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
