import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Force test sqlite database before importing app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_taskforge.db"
os.environ["SECRET_KEY"] = "test-secret-key-taskforge-production-grade-12345"

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.enums import UserRole, TaskStatus, TaskPriority
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
import uuid

test_engine = create_async_engine("sqlite+aiosqlite:///./test_taskforge.db", echo=False)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed initial test data
    async with TestingSessionLocal() as session:
        admin_user = User(
            id=uuid.UUID("a1111111-1111-1111-1111-111111111111"),
            email="dev@taskforge.dev",
            password_hash=get_password_hash("SecurePassword123!"),
            full_name="Dev Admin",
            role=UserRole.admin,
            is_active=True
        )
        member_user = User(
            id=uuid.UUID("a3bb189e-8bf9-3888-9912-ace4e6543002"),
            email="member@taskforge.dev",
            password_hash=get_password_hash("SecurePassword123!"),
            full_name="Member Charlie",
            role=UserRole.member,
            is_active=True
        )
        session.add_all([admin_user, member_user])
        await session.flush()

        test_project = Project(
            id=uuid.UUID("b1111111-1111-1111-1111-111111111111"),
            title="Core Platform",
            slug="core-platform",
            description="Core engineering tasks",
            owner_id=admin_user.id
        )
        session.add(test_project)
        await session.flush()

        test_task = Task(
            id=uuid.UUID("c1111111-1111-1111-1111-111111111111"),
            project_id=test_project.id,
            assignee_id=admin_user.id,
            title="Implement Auth Pipeline",
            description="JWT Access/Refresh token rotation",
            status=TaskStatus.todo,
            priority=TaskPriority.urgent
        )
        session.add(test_task)
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    if os.path.exists("./test_taskforge.db"):
        try:
            os.remove("./test_taskforge.db")
        except Exception:
            pass


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def admin_token():
    return create_access_token(
        subject="a1111111-1111-1111-1111-111111111111",
        role="admin",
        email="dev@taskforge.dev"
    )


@pytest.fixture
def member_token():
    return create_access_token(
        subject="a3bb189e-8bf9-3888-9912-ace4e6543002",
        role="member",
        email="member@taskforge.dev"
    )
