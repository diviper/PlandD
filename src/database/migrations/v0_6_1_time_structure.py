"""Migration for v0.6.1 - Adding time structure to plans"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy import String, Integer, DateTime, Time, JSON, Float, Enum, ForeignKey

# Создаем временные enum типы для миграции
time_block = sa.Enum('morning', 'afternoon', 'evening', name='timeblock')
priority = sa.Enum('high', 'medium', 'low', name='priority')

def upgrade():
    # Создаем новые таблицы
    op.create_table(
        'plans_v2',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('user_id', Integer, nullable=False),
        sa.Column('title', String, nullable=False),
        sa.Column('description', String),
        sa.Column('time_block', time_block, nullable=False),
        sa.Column('start_time', Time, nullable=False),
        sa.Column('end_time', Time, nullable=False),
        sa.Column('duration_minutes', Integer, nullable=False),
        sa.Column('priority', priority, nullable=False),
        sa.Column('status', String, default='active'),
        sa.Column('created_at', DateTime, default=datetime.utcnow),
        sa.Column('updated_at', DateTime, onupdate=datetime.utcnow),
        sa.Column('deadline', DateTime),
    )

    op.create_table(
        'plan_steps_v2',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('plan_id', Integer, ForeignKey('plans_v2.id'), nullable=False),
        sa.Column('title', String, nullable=False),
        sa.Column('description', String),
        sa.Column('start_time', Time),
        sa.Column('end_time', Time),
        sa.Column('duration_minutes', Integer),
        sa.Column('priority', priority),
        sa.Column('status', String, default='pending'),
        sa.Column('created_at', DateTime, default=datetime.utcnow),
        sa.Column('metrics', JSON),
    )

    op.create_table(
        'plan_progress_v2',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('plan_id', Integer, ForeignKey('plans_v2.id'), nullable=False),
        sa.Column('step_id', Integer, ForeignKey('plan_steps_v2.id'), nullable=False),
        sa.Column('started_at', DateTime),
        sa.Column('completed_at', DateTime),
        sa.Column('actual_duration_minutes', Integer),
        sa.Column('status', String, nullable=False),
        sa.Column('notes', String),
        sa.Column('blockers', JSON),
        sa.Column('timestamp', DateTime, default=datetime.utcnow),
    )

    op.create_table(
        'user_preferences_v2',
        sa.Column('id', Integer, primary_key=True),
        sa.Column('user_id', Integer, nullable=False, unique=True),
        sa.Column('work_hours', JSON),
        sa.Column('time_blocks', JSON),
        sa.Column('break_preferences', JSON),
        sa.Column('default_priority', priority, default='medium'),
        sa.Column('humor_level', Integer, default=20),
        sa.Column('notification_style', String, default='balanced'),
        sa.Column('productivity_hours', JSON),
        sa.Column('completion_rates', JSON),
        sa.Column('task_patterns', JSON),
        sa.Column('created_at', DateTime, default=datetime.utcnow),
        sa.Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('last_analysis', DateTime),
        sa.Column('ai_confidence', Float, default=0.5),
    )

    # Создаем индексы
    op.create_index('idx_plans_v2_user_id', 'plans_v2', ['user_id'])
    op.create_index('idx_plans_v2_time_block', 'plans_v2', ['time_block'])
    op.create_index('idx_plans_v2_priority', 'plans_v2', ['priority'])
    op.create_index('idx_plan_steps_v2_plan_id', 'plan_steps_v2', ['plan_id'])
    op.create_index('idx_plan_progress_v2_plan_id', 'plan_progress_v2', ['plan_id'])
    op.create_index('idx_plan_progress_v2_step_id', 'plan_progress_v2', ['step_id'])

def downgrade():
    # Удаляем таблицы в обратном порядке
    op.drop_table('user_preferences_v2')
    op.drop_table('plan_progress_v2')
    op.drop_table('plan_steps_v2')
    op.drop_table('plans_v2')
    
    # Удаляем enum типы
    time_block.drop(op.get_bind())
    priority.drop(op.get_bind())
