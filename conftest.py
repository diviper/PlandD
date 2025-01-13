"""Pytest configuration"""
import os
import sys
import pytest
import asyncio
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.models_v2 import Base, User, UserPreferences, TimeBlock, Priority
from src.services.plan_service_v2 import PlanServiceV2
from src.services.ai.ai_service import AIService

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db"

# Counter для генерации уникальных telegram_id
_telegram_id_counter = 0

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture(scope="session")
async def async_session_factory(engine):
    """Create a test database session factory."""
    return sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

@pytest.fixture
async def session(async_session_factory):
    """Create a test database session."""
    async with async_session_factory() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_user(session):
    """Create a test user with preferences."""
    global _telegram_id_counter
    _telegram_id_counter += 1
    
    # Создаем пользователя с уникальным telegram_id
    user = User(
        telegram_id=123456789 + _telegram_id_counter,
        username=f"test_user_{_telegram_id_counter}",
        first_name="Test",
        last_name="User",
        language_code="en",
        is_premium=False,
        created_at=datetime.utcnow()
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Создаем предпочтения пользователя
    preferences = UserPreferences(
        user_id=user.id,
        work_hours=json.dumps({
            "start": "09:00",
            "end": "18:00"
        }),
        time_blocks=json.dumps({
            "morning": True,
            "afternoon": True,
            "evening": True
        }),
        break_preferences=json.dumps({
            "duration": 15,
            "frequency": 120
        }),
        default_priority=Priority.MEDIUM,
        humor_level=20,
        notification_style="balanced",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(preferences)
    await session.commit()

    return user

@pytest.fixture
async def plan_service(session):
    """Create a plan service instance."""
    return PlanServiceV2(session)

@pytest.fixture
async def ai_service(session):
    """Create an AI service instance."""
    return AIService(session)
