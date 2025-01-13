"""Test error handling"""
import pytest
from datetime import datetime, time
from src.services.plan_service_v2 import PlanServiceV2
from src.services.ai.ai_service import AIService
from src.database.models_v2 import Plan, TimeBlock, Priority
from src.core.exceptions import (
    InvalidTimeFormat,
    TimeConflictError,
    PlanNotFoundError,
    AIServiceError
)

@pytest.mark.asyncio
async def test_invalid_time_format(plan_service):
    """Test handling of invalid time format"""
    with pytest.raises(InvalidTimeFormat):
        await plan_service.create_plan(
            user_id=1,
            plan_text="Test plan",
            start_time="25:00"  # Invalid time
        )

@pytest.mark.asyncio
async def test_time_conflict(plan_service):
    """Test handling of time conflicts"""
    # Create first plan
    await plan_service.create_plan(
        user_id=1,
        plan_text="First plan",
        start_time="10:00"
    )
    
    # Try to create overlapping plan
    with pytest.raises(TimeConflictError):
        await plan_service.create_plan(
            user_id=1,
            plan_text="Second plan",
            start_time="10:30"
        )

@pytest.mark.asyncio
async def test_plan_not_found(plan_service):
    """Test handling of non-existent plan"""
    with pytest.raises(PlanNotFoundError):
        await plan_service.get_plan(999)  # Non-existent ID

@pytest.mark.asyncio
async def test_ai_service_error(ai_service):
    """Test handling of AI service errors"""
    with pytest.raises(AIServiceError):
        await ai_service.analyze_plan(None)  # Invalid input

@pytest.mark.asyncio
async def test_empty_plan_text(plan_service):
    """Test handling of empty plan text"""
    with pytest.raises(ValueError):
        await plan_service.create_plan(
            user_id=1,
            plan_text="",
            start_time="10:00"
        )

@pytest.mark.asyncio
async def test_past_time(plan_service):
    """Test handling of past time"""
    current_time = datetime.now().time()
    past_time = (datetime.now().replace(hour=current_time.hour-1)).strftime("%H:%M")
    
    with pytest.raises(ValueError):
        await plan_service.create_plan(
            user_id=1,
            plan_text="Test plan",
            start_time=past_time
        )

@pytest.mark.asyncio
async def test_invalid_user_id(plan_service):
    """Test handling of invalid user ID"""
    with pytest.raises(ValueError):
        await plan_service.create_plan(
            user_id=-1,  # Invalid ID
            plan_text="Test plan",
            start_time="10:00"
        )

@pytest.mark.asyncio
async def test_too_long_plan(plan_service):
    """Test handling of too long plan text"""
    long_text = "A" * 1001  # More than 1000 characters
    with pytest.raises(ValueError):
        await plan_service.create_plan(
            user_id=1,
            plan_text=long_text,
            start_time="10:00"
        )

@pytest.mark.asyncio
async def test_invalid_step_order(plan_service):
    """Test handling of invalid step order"""
    with pytest.raises(ValueError):
        await plan_service.create_plan(
            user_id=1,
            plan_text="""
            План
            3. Третий шаг
            1. Первый шаг
            """,
            start_time="10:00"
        )

@pytest.mark.asyncio
async def test_duplicate_steps(plan_service):
    """Test handling of duplicate steps"""
    with pytest.raises(ValueError):
        await plan_service.create_plan(
            user_id=1,
            plan_text="""
            План
            - Шаг 1
            - Шаг 1
            """,
            start_time="10:00"
        )

@pytest.mark.asyncio
async def test_invalid_priority(plan_service):
    """Test handling of invalid priority"""
    with pytest.raises(ValueError):
        await plan_service.create_plan(
            user_id=1,
            plan_text="План !!!!!!!!!",  # Too many priority markers
            start_time="10:00"
        )

@pytest.mark.asyncio
async def test_concurrent_modifications(plan_service):
    """Test handling of concurrent modifications"""
    # Create a plan
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text="Test plan",
        start_time="10:00"
    )
    
    # Try to update the same plan concurrently
    async def update_plan():
        await plan_service.update_plan(
            plan_id=plan.id,
            new_title="Updated plan"
        )
    
    # Run updates concurrently
    with pytest.raises(Exception):  # Should handle concurrent modifications
        await asyncio.gather(update_plan(), update_plan())

@pytest.mark.asyncio
async def test_invalid_time_block(plan_service):
    """Test handling of invalid time block"""
    with pytest.raises(ValueError):
        await plan_service.create_plan(
            user_id=1,
            plan_text="Test plan",
            start_time="03:00"  # Time outside of valid blocks
        )
