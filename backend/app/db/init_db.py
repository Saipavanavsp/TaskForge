import logging
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import engine, async_session_factory
from app.models.enums import UserRole, TaskStatus, TaskPriority
from app.models.user import User
from app.models.project import Project
from app.models.task import Task

logger = logging.getLogger("taskforge.init_db")


async def init_database():
    async with engine.begin() as conn:
        # Create tables if not exist
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Check if users already exist
        result = await session.execute(select(User).limit(1))
        existing_user = result.scalars().first()
        if existing_user:
            logger.info("Database already initialized.")
            return

        logger.info("Seeding initial database...")
        
        # 1. Create Core Users
        dev_admin = User(
            id=uuid.UUID("a1111111-1111-1111-1111-111111111111"),
            email="dev@taskforge.dev",
            password_hash=get_password_hash("SecurePassword123!"),
            full_name="Alex Mercer (Admin)",
            role=UserRole.admin,
            is_active=True
        )
        
        manager = User(
            id=uuid.UUID("a2222222-2222-2222-2222-222222222222"),
            email="manager@taskforge.dev",
            password_hash=get_password_hash("SecurePassword123!"),
            full_name="Sarah Connor (Manager)",
            role=UserRole.manager,
            is_active=True
        )

        member = User(
            id=uuid.UUID("a3bb189e-8bf9-3888-9912-ace4e6543002"),
            email="member@taskforge.dev",
            password_hash=get_password_hash("SecurePassword123!"),
            full_name="Charlie Kent (Member)",
            role=UserRole.member,
            is_active=True
        )

        session.add_all([dev_admin, manager, member])
        await session.flush()

        # 2. Create Core Project
        proj_main = Project(
            id=uuid.UUID("b1111111-1111-1111-1111-111111111111"),
            title="Core Infrastructure & Platform",
            slug="core-infrastructure",
            description="Enterprise cloud architecture, auth flows, and real-time distributed sync engine.",
            owner_id=dev_admin.id
        )
        proj_mobile = Project(
            id=uuid.UUID("b2222222-2222-2222-2222-222222222222"),
            title="Client Mobile & Edge",
            slug="client-mobile-edge",
            description="Cross-platform responsive frontend and offline sync components.",
            owner_id=manager.id
        )
        session.add_all([proj_main, proj_mobile])
        await session.flush()

        # 3. Create Core Tasks
        now = datetime.now(timezone.utc)
        tasks = [
            Task(
                id=uuid.UUID("c1111111-1111-1111-1111-111111111111"),
                project_id=proj_main.id,
                assignee_id=dev_admin.id,
                title="Implement Auth Pipeline",
                description="JWT-based Access/Refresh Token rotation with Argon2id password hashing and RBAC middleware.",
                status=TaskStatus.todo,
                priority=TaskPriority.urgent,
                due_date=now + timedelta(days=2)
            ),
            Task(
                id=uuid.UUID("c2222222-2222-2222-2222-222222222222"),
                project_id=proj_main.id,
                assignee_id=manager.id,
                title="Configure Traefik & Rate Limiting",
                description="Setup Traefik reverse proxy with TLS termination and IP-based rate limiting.",
                status=TaskStatus.in_progress,
                priority=TaskPriority.high,
                due_date=now + timedelta(days=4)
            ),
            Task(
                id=uuid.UUID("c3333333-3333-3333-3333-333333333333"),
                project_id=proj_main.id,
                assignee_id=member.id,
                title="Real-time Socket Server Integration",
                description="Cluster Node.js real-time Socket.io engine with Redis pub/sub broker.",
                status=TaskStatus.in_review,
                priority=TaskPriority.medium,
                due_date=now + timedelta(days=5)
            ),
            Task(
                id=uuid.UUID("c4444444-4444-4444-4444-444444444444"),
                project_id=proj_main.id,
                assignee_id=dev_admin.id,
                title="PostgreSQL 16 Schema Migrations",
                description="Alembic versioned migrations with UUID primary keys and composite indexes.",
                status=TaskStatus.completed,
                priority=TaskPriority.medium,
                due_date=now - timedelta(days=1)
            ),
            Task(
                id=uuid.UUID("c5555555-5555-5555-5555-555555555555"),
                project_id=proj_main.id,
                assignee_id=member.id,
                title="Setup OpenTelemetry & Prometheus Exporter",
                description="Instrument FastAPI handlers and export metrics on /metrics for Prometheus scraping.",
                status=TaskStatus.todo,
                priority=TaskPriority.low,
                due_date=now + timedelta(days=7)
            )
        ]
        session.add_all(tasks)
        await session.commit()
        logger.info("Database seeding complete!")
