"""Test plan service functionality"""
import pytest
from datetime import datetime, time
from src.services.plan_service_v2 import PlanServiceV2
from src.database.models_v2 import Plan, TimeBlock, Priority, PlanStep, User
from src.database.database import Database
from src.core.exceptions import PlanNotFoundError, InvalidTimeFormatError, TimeConflictError, InvalidPriorityError

@pytest.fixture
def db():
    """Database fixture"""
    return Database()

@pytest.fixture
def plan_service(db):
    """Plan service fixture"""
    return PlanServiceV2(db.get_session())

@pytest.fixture
def test_user():
    """Test user fixture"""
    # Replace with actual test user creation logic
    return User(id=1)

@pytest.mark.asyncio
async def test_create_plan(plan_service, test_user):
    """Test plan creation"""
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
    assert plan.title == plan_data["title"]
    assert plan.time_block == plan_data["time_block"]
    assert plan.priority == plan_data["priority"]

@pytest.mark.asyncio
async def test_get_user_plans(plan_service, test_user):
    """Test getting user plans"""
    # Create test plan
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
    
    # Get plans
    plans = await plan_service.get_user_plans(test_user.id)
    assert len(plans) > 0
    assert plans[0].title == plan_data["title"]

@pytest.mark.asyncio
async def test_update_plan(plan_service, test_user):
    """Test plan update"""
    # Create test plan
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
    
    # Update plan
    update_data = {
        "title": "Updated Plan",
        "priority": Priority.HIGH
    }
    updated_plan = await plan_service.update_plan(plan.id, update_data)
    assert updated_plan.title == update_data["title"]
    assert updated_plan.priority == update_data["priority"]

@pytest.mark.asyncio
async def test_delete_plan(plan_service, test_user):
    """Test plan deletion"""
    # Create test plan
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
    
    # Delete plan
    await plan_service.delete_plan(plan.id)
    
    # Try to get deleted plan
    with pytest.raises(PlanNotFoundError):
        await plan_service.get_plan(plan.id)

@pytest.mark.asyncio
async def test_check_conflicts(plan_service, test_user):
    """Test time conflict checking"""
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
        "start_time": time(9, 30),
        "end_time": time(10, 30),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    with pytest.raises(TimeConflictError):
        await plan_service.create_plan(test_user.id, plan_data2)

@pytest.mark.asyncio
async def test_plan_steps(plan_service, test_user):
    """Test plan steps management"""
    # Create plan with steps
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
                "order": 1
            },
            {
                "title": "Step 2",
                "description": "Second step",
                "duration_minutes": 30,
                "order": 2
            }
        ]
    }
    plan = await plan_service.create_plan(test_user.id, plan_data)
    assert len(plan.steps) == 2
    assert plan.steps[0].title == "Step 1"
    assert plan.steps[1].title == "Step 2"

@pytest.mark.asyncio
async def test_validate_time(plan_service):
    """Test time validation"""
    # Проверяем корректное время
    assert await plan_service.validate_time("09:00") == time(9, 0)
    assert await plan_service.validate_time("23:59") == time(23, 59)
    
    # Проверяем некорректное время
    with pytest.raises(InvalidTimeFormatError):
        await plan_service.validate_time("24:00")
    with pytest.raises(InvalidTimeFormatError):
        await plan_service.validate_time("09:60")
    with pytest.raises(InvalidTimeFormatError):
        await plan_service.validate_time("9:00")  # Должно быть "09:00"

@pytest.mark.asyncio
async def test_get_time_block(plan_service):
    """Test time block determination"""
    assert await plan_service.get_time_block("06:00") == TimeBlock.MORNING
    assert await plan_service.get_time_block("09:00") == TimeBlock.MORNING
    assert await plan_service.get_time_block("12:00") == TimeBlock.AFTERNOON
    assert await plan_service.get_time_block("15:00") == TimeBlock.AFTERNOON
    assert await plan_service.get_time_block("18:00") == TimeBlock.EVENING
    assert await plan_service.get_time_block("21:00") == TimeBlock.EVENING

@pytest.mark.asyncio
async def test_estimate_duration(plan_service):
    """Test duration estimation"""
    plan_data = {
        "title": "Test Plan",
        "description": "A simple plan with steps",
        "steps": [
            {
                "title": "Step 1",
                "description": "First step",
                "duration_minutes": 30
            },
            {
                "title": "Step 2",
                "description": "Second step",
                "duration_minutes": 45
            }
        ]
    }
    
    duration = await plan_service.estimate_duration(plan_data)
    assert duration == 75  # 30 + 45 минут

@pytest.mark.asyncio
async def test_check_conflicts(plan_service, test_user):
    """Test time conflict checking"""
    # Создаем первый план
    plan_data1 = {
        "title": "First Plan",
        "description": "First Description",
        "time_block": TimeBlock.MORNING,
        "start_time": time(9, 0),
        "end_time": time(10, 0),
        "duration_minutes": 60,
        "priority": Priority.MEDIUM
    }
    
    await plan_service.create_plan(test_user.id, plan_data1)
    
    # Проверяем конфликты
    assert await plan_service.check_conflicts(
        test_user.id,
        time(9, 30),  # Конфликт
        time(10, 30)
    ) == True
    
    assert await plan_service.check_conflicts(
        test_user.id,
        time(10, 0),  # Нет конфликта
        time(11, 0)
    ) == False

@pytest.mark.asyncio
async def test_plan_steps(plan_service, test_user):
    """Test plan steps management"""
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
                "order": 1,
                "duration_minutes": 30
            },
            {
                "title": "Step 2",
                "description": "Second step",
                "order": 2,
                "duration_minutes": 30
            }
        ]
    }
    
    plan = await plan_service.create_plan(test_user.id, plan_data)
    
    # Проверяем шаги
    assert len(plan.steps) == 2
    assert plan.steps[0].order == 1
    assert plan.steps[1].order == 2
    
    # Обновляем шаг
    step_update = {
        "title": "Updated Step 1",
        "duration_minutes": 45
    }
    
    updated_plan = await plan_service.update_plan_step(plan.id, plan.steps[0].id, step_update)
    assert updated_plan.steps[0].title == "Updated Step 1"
    assert updated_plan.steps[0].duration_minutes == 45
    
    # Удаляем шаг
    updated_plan = await plan_service.delete_plan_step(plan.id, plan.steps[1].id)
    assert len(updated_plan.steps) == 1
