"""Add premium features

Revision ID: v0_7_0
Revises: v0_6_0
Create Date: 2024-01-13 13:54:02.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'v0_7_0'
down_revision = 'v0_6_0'
branch_labels = None
depends_on = None

def upgrade():
    # Создаем enum типы
    op.execute("CREATE TYPE interaction_style AS ENUM ('rick', 'strict', 'minimal', 'friendly', 'anime', 'custom')")
    op.execute("CREATE TYPE calendar_type AS ENUM ('google', 'outlook', 'apple', 'custom')")
    
    # UserProfile
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('coins', sa.Integer(), nullable=False, default=0),
        sa.Column('interaction_style', sa.Enum('rick', 'strict', 'minimal', 'friendly', 'anime', 'custom', name='interaction_style'), nullable=False),
        sa.Column('premium_until', sa.DateTime(), nullable=True),
        sa.Column('active_sticker_pack', sa.Integer(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # CalendarConnection
    op.create_table(
        'calendar_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_profile_id', sa.Integer(), nullable=False),
        sa.Column('calendar_type', sa.Enum('google', 'outlook', 'apple', 'custom', name='calendar_type'), nullable=False),
        sa.Column('calendar_id', sa.String(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=False),
        sa.Column('token_expires', sa.DateTime(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False),
        sa.Column('sync_enabled', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['user_profile_id'], ['user_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # CalendarEvent
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('calendar_id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('is_all_day', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, default=False),
        sa.Column('recurrence_rule', sa.String(), nullable=True),
        sa.Column('importance', sa.Integer(), nullable=False, default=1),
        sa.ForeignKeyConstraint(['calendar_id'], ['calendar_connections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # StickerPack
    op.create_table(
        'sticker_packs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('is_premium', sa.Boolean(), nullable=False, default=False),
        sa.Column('stickers', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # UserStickerPack
    op.create_table(
        'user_sticker_packs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_profile_id', sa.Integer(), nullable=False),
        sa.Column('sticker_pack_id', sa.Integer(), nullable=False),
        sa.Column('purchased_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_profile_id'], ['user_profiles.id'], ),
        sa.ForeignKeyConstraint(['sticker_pack_id'], ['sticker_packs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # CoinTransaction
    op.create_table(
        'coin_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_profile_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_profile_id'], ['user_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Gift
    op.create_table(
        'gifts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('from_user_id', sa.Integer(), nullable=False),
        sa.Column('to_user_id', sa.Integer(), nullable=False),
        sa.Column('item_type', sa.String(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=True),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_anonymous', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['from_user_id'], ['user_profiles.id'], ),
        sa.ForeignKeyConstraint(['to_user_id'], ['user_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Обновляем существующие таблицы
    
    # Plan
    op.add_column('plans', sa.Column('calendar_event_id', sa.Integer(), nullable=True))
    op.add_column('plans', sa.Column('is_flexible', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('plans', sa.Column('reminder_times', sa.JSON(), nullable=True))
    op.add_column('plans', sa.Column('completion_reward', sa.Integer(), nullable=False, server_default='10'))
    op.create_foreign_key(None, 'plans', 'calendar_events', ['calendar_event_id'], ['id'])
    
    # PlanStep
    op.add_column('plan_steps', sa.Column('completion_reward', sa.Integer(), nullable=False, server_default='5'))

def downgrade():
    # Удаляем обновления существующих таблиц
    op.drop_column('plan_steps', 'completion_reward')
    op.drop_column('plans', 'completion_reward')
    op.drop_column('plans', 'reminder_times')
    op.drop_column('plans', 'is_flexible')
    op.drop_column('plans', 'calendar_event_id')
    
    # Удаляем новые таблицы
    op.drop_table('gifts')
    op.drop_table('coin_transactions')
    op.drop_table('user_sticker_packs')
    op.drop_table('sticker_packs')
    op.drop_table('calendar_events')
    op.drop_table('calendar_connections')
    op.drop_table('user_profiles')
    
    # Удаляем enum типы
    op.execute('DROP TYPE calendar_type')
    op.execute('DROP TYPE interaction_style')
