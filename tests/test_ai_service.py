"""Tests for AI service"""
import pytest
from datetime import datetime, time
import json

from src.database.models_v2 import User, Plan, TimeBlock, Priority
from src.services.ai.ai_service import AIService
from src.services.plan_service_v2 import PlanServiceV2
from src.core.exceptions import AIServiceError

@pytest.fixture
def ai_service():
    """AI service fixture"""
    return AIService()

@pytest.fixture
def test_user():
    """Test user fixture"""
    # Create a test user
    user = User(id=1, name="Test User")
    return user

@pytest.fixture
def plan_service():
    """Plan service fixture"""
    return PlanServiceV2()

@pytest.fixture
def session():
    """Session fixture"""
    return Session()

@pytest.mark.asyncio
async def test_analyze_plan_text(session, test_user, ai_service):
    """Test plan text analysis"""
    # Test with valid text
    result = await ai_service.analyze_plan_text("Meeting with team at 10:00")
    assert isinstance(result, dict)
    assert "title" in result
    assert "time_block" in result
    assert "duration_minutes" in result
    assert "priority" in result

    # Test with empty text
    with pytest.raises(AIServiceError):
        await ai_service.analyze_plan_text("")

@pytest.mark.asyncio
async def test_suggest_time_block(session, test_user, ai_service):
    """Test time block suggestions"""
    plan_data = {
        "title": "Morning Meeting",
        "description": "Team sync-up",
        "start_time": time(9, 0),
        "end_time": time(10, 0)
    }
    
    time_block = await ai_service.suggest_time_block(test_user.id, plan_data)
    assert isinstance(time_block, TimeBlock)

@pytest.mark.asyncio
async def test_suggest_priority(session, test_user, ai_service):
    """Test priority suggestions"""
    plan_data = {
        "title": "Urgent Client Meeting",
        "description": "Discussion of critical issues"
    }
    
    priority = await ai_service.suggest_priority(test_user.id, plan_data)
    assert isinstance(priority, Priority)

@pytest.mark.asyncio
async def test_suggest_steps(session, test_user, ai_service):
    """Test step suggestions"""
    plan_text = "Prepare presentation for client meeting"
    steps = await ai_service.suggest_steps(plan_text)
    
    assert isinstance(steps, list)
    assert len(steps) > 0
    assert all("title" in step for step in steps)
    assert all("duration_minutes" in step for step in steps)
    assert all("order" in step for step in steps)

@pytest.mark.asyncio
async def test_get_daily_summary(session, test_user, ai_service, plan_service):
    """Test daily summary generation"""
    # Create some test plans
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    await plan_service.create_plan(test_user.id, plan_data)
    
    summary = await ai_service.get_daily_summary(test_user.id, datetime.utcnow())
    assert isinstance(summary, str)
    assert len(summary) > 0

@pytest.mark.asyncio
async def test_get_weekly_analysis(session, test_user, ai_service, plan_service):
    """Test weekly analysis generation"""
    # Create some test plans
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    await plan_service.create_plan(test_user.id, plan_data)
    
    analysis = await ai_service.get_weekly_analysis(test_user.id, datetime.utcnow())
    assert isinstance(analysis, dict)
    assert "total_plans" in analysis
    assert "time_blocks" in analysis
    assert "priorities" in analysis
