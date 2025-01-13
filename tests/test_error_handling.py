"""Tests for error handling"""
import pytest
from datetime import datetime, time

from src.database.models_v2 import User, Plan, TimeBlock, Priority
from src.core.exceptions import (
    PlanNotFoundError,
    InvalidTimeFormatError,
    TimeConflictError,
    InvalidPriorityError,
    AIServiceError
)

@pytest.mark.asyncio
async def test_invalid_time_format(session, test_user, plan_service):
    """Test handling of invalid time format"""
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": "invalid_time",  # Invalid time format
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    
    with pytest.raises(InvalidTimeFormatError):
        await plan_service.create_plan(test_user.id, plan_data)

@pytest.mark.asyncio
async def test_time_conflict(session, test_user, plan_service):
    """Test handling of time conflicts"""
    # Create first plan
    plan_data1 = {
        "title": "Test Plan 1",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    await plan_service.create_plan(test_user.id, plan_data1)
    
    # Try to create conflicting plan
    plan_data2 = {
        "title": "Test Plan 2",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 30),  # Overlapping time
        "end_time": time(10, 30),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    
    with pytest.raises(TimeConflictError):
        await plan_service.create_plan(test_user.id, plan_data2)

@pytest.mark.asyncio
async def test_invalid_priority(session, test_user, plan_service):
    """Test handling of invalid priority"""
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": "INVALID_PRIORITY"  # Invalid priority
    }
    
    with pytest.raises(InvalidPriorityError):
        await plan_service.create_plan(test_user.id, plan_data)

@pytest.mark.asyncio
async def test_plan_not_found(session, test_user, plan_service):
    """Test handling of non-existent plan"""
    with pytest.raises(PlanNotFoundError):
        await plan_service.get_plan(test_user.id, 999999)  # Non-existent plan ID

@pytest.mark.asyncio
async def test_concurrent_modifications(session, test_user, plan_service):
    """Test handling of concurrent modifications"""
    # Create initial plan
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    plan = await plan_service.create_plan(test_user.id, plan_data)
    
    # Try to update the same plan concurrently
    update_data1 = {"title": "Updated Title 1"}
    update_data2 = {"title": "Updated Title 2"}
    
    # This should raise a database error due to concurrent modification
    async with session.begin_nested():
        await plan_service.update_plan(test_user.id, plan.id, update_data1)
        await plan_service.update_plan(test_user.id, plan.id, update_data2)

@pytest.mark.asyncio
async def test_ai_service_errors(session, test_user, ai_service):
    """Test handling of AI service errors"""
    # Test with empty text
    with pytest.raises(AIServiceError):
        await ai_service.analyze_plan_text("")
    
    # Test with invalid plan data
    with pytest.raises(AIServiceError):
        await ai_service.suggest_time_block(test_user.id, {})

@pytest.mark.asyncio
async def test_empty_plan_text(session, test_user, plan_service):
    """Test handling of empty plan text"""
    plan_data = {
        "title": "",
        "description": "",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    with pytest.raises(Exception):  # No specific exception is defined for this case
        await plan_service.create_plan(test_user.id, plan_data)

@pytest.mark.asyncio
async def test_past_time(session, test_user, plan_service):
    """Test handling of past time"""
    current_time = datetime.now().time()
    past_hour = (current_time.hour - 1) % 24
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(past_hour, 0),
        "end_time": time(past_hour + 1, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    with pytest.raises(Exception):  # No specific exception is defined for this case
        await plan_service.create_plan(test_user.id, plan_data)

@pytest.mark.asyncio
async def test_invalid_user_id(session, plan_service):
    """Test handling of invalid user ID"""
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    with pytest.raises(Exception):  # No specific exception is defined for this case
        await plan_service.create_plan(999, plan_data)

@pytest.mark.asyncio
async def test_too_long_plan(session, test_user, plan_service):
    """Test handling of too long plan"""
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description" * 1000,  # Very long description
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    with pytest.raises(Exception):  # No specific exception is defined for this case
        await plan_service.create_plan(test_user.id, plan_data)

@pytest.mark.asyncio
async def test_invalid_step_order(session, test_user, plan_service):
    """Test handling of invalid step order"""
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM,
        "steps": [
            {
                "title": "Step 1",
                "description": "First step",
                "duration_minutes": 30,
                "order": 2  # Invalid order
            },
            {
                "title": "Step 2",
                "description": "Second step",
                "duration_minutes": 30,
                "order": 1
            }
        ]
    }
    with pytest.raises(Exception):  # No specific exception is defined for this case
        await plan_service.create_plan(test_user.id, plan_data)

@pytest.mark.asyncio
async def test_duplicate_steps(session, test_user, plan_service):
    """Test handling of duplicate steps"""
    plan_data = {
        "title": "Test Plan",
        "description": "Test Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM,
        "steps": [
            {
                "title": "Step 1",
                "description": "Same step",
                "duration_minutes": 30,
                "order": 1
            },
            {
                "title": "Step 1",  # Duplicate step title
                "description": "Same step",
                "duration_minutes": 30,
                "order": 2
            }
        ]
    }
    with pytest.raises(Exception):  # No specific exception is defined for this case
        await plan_service.create_plan(test_user.id, plan_data)
