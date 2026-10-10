"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-10 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=False)

    # 2. Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('slug', sa.String(length=180), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )

    # 3. Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('assignee_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='todo'),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='medium'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_tasks_project_id', 'tasks', ['project_id'], unique=False)
    op.create_index('idx_tasks_status', 'tasks', ['status'], unique=False)
    op.create_index('idx_tasks_assignee_id', 'tasks', ['assignee_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_tasks_assignee_id', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')
    op.drop_index('idx_tasks_project_id', table_name='tasks')
    op.drop_table('tasks')
    op.drop_table('projects')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
