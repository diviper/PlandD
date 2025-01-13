"""Pytest configuration file"""
import os
import sys
from pathlib import Path
import pytest
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.database import Database
from src.database.models_v2 import User, UserPreferences, UserProfile
from src.services.ai.ai_service import AIService
from src.services.plan_service_v2 import PlanServiceV2

@pytest.fixture
def db():
    """Database fixture"""
    database = Database()
    return database

@pytest.fixture
def test_user(db):
    """Create test user"""
    user = User(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
        last_name="User",
        language_code="en"
    )
    
    # Создаем предпочтения пользователя
    preferences = UserPreferences(
        work_hours={"start": "09:00", "end": "18:00"},
        time_blocks={"morning": True, "afternoon": True, "evening": True},
        break_preferences={"duration": 15, "frequency": 120}
    )
    user.preferences = preferences
    
    # Создаем профиль пользователя
    profile = UserProfile(
        coins=100,
        interaction_style="rick"
    )
    user.profile = profile
    
    session = db.get_session()
    session.add(user)
    session.commit()
    
    yield user
    
    # Очистка после тестов
    session.query(User).delete()
    session.commit()

@pytest.fixture
def ai_service(db):
    """AI service fixture"""
    return AIService(db)

@pytest.fixture
def plan_service(db):
    """Plan service fixture"""
    return PlanServiceV2(db)
