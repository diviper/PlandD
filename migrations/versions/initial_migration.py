"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-01-11 19:15:11.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('parent_task_id', sa.Integer(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('energy_level', sa.Integer(), nullable=True),
        sa.Column('energy_type', sa.String(), nullable=True),
        sa.Column('optimal_time', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('focus_required', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create schedules table
    op.create_table('schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sleep_time', sa.String(), nullable=True),
        sa.Column('wake_time', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create meals table
    op.create_table('meals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('meal_time', sa.String(), nullable=False),
        sa.Column('meal_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create reminder_settings table
    op.create_table('reminder_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('default_reminder_time', sa.Integer(), default=30),
        sa.Column('morning_reminder_time', sa.String(), default='09:00'),
        sa.Column('evening_reminder_time', sa.String(), default='20:00'),
        sa.Column('priority_high_interval', sa.Integer(), default=30),
        sa.Column('priority_medium_interval', sa.Integer(), default=60),
        sa.Column('priority_low_interval', sa.Integer(), default=120),
        sa.Column('quiet_hours_start', sa.String(), default='23:00'),
        sa.Column('quiet_hours_end', sa.String(), default='07:00'),
        sa.Column('reminder_types', sa.String(), default='all'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

def downgrade() -> None:
    op.drop_table('reminder_settings')
    op.drop_table('meals')
    op.drop_table('schedules')
    op.drop_table('tasks')
