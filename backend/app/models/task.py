import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID
from app.models.enums import TaskPriority, TaskStatus

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )
    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status", native_enum=False),
        default=TaskStatus.todo,
        nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority", native_enum=False),
        default=TaskPriority.medium,
        nullable=False
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks"
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="tasks"
    )

    __table_args__ = (
        Index("idx_tasks_project_id", "project_id"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_assignee_id", "assignee_id"),
    )
