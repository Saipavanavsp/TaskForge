from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    member = "member"


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    in_review = "in_review"
    completed = "completed"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"
