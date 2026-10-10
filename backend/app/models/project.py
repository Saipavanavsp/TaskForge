import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(180),
        unique=True,
        index=True,
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    owner: Mapped["User"] = relationship(
        "User",
        back_populates="projects"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )
