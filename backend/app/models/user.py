import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import Boolean, DateTime, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.task import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.member,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
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

    projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="assignee"
    )

    __table_args__ = (
        Index("idx_users_email", "email"),
    )
