"""Test plan service functionality"""
import pytest
from datetime import datetime, time
from src.services.plan_service_v2 import PlanServiceV2
from src.database.models_v2 import Plan, TimeBlock, Priority, PlanStep
from src.database.database import Database

@pytest.fixture
def db():
    """Database fixture"""
    return Database()

@pytest.fixture
def plan_service(db):
    """Plan service fixture"""
    return PlanServiceV2(db.get_session())

def test_validate_time():
    """Test time validation"""
    assert PlanServiceV2.validate_time("09:00") == True
    assert PlanServiceV2.validate_time("25:00") == False
    assert PlanServiceV2.validate_time("09:60") == False
    assert PlanServiceV2.validate_time("9:00") == False  # Должно быть "09:00"
    assert PlanServiceV2.validate_time("0900") == False

def test_get_time_block():
    """Test time block determination"""
    assert PlanServiceV2.get_time_block(time(9, 0)) == TimeBlock.MORNING
    assert PlanServiceV2.get_time_block(time(14, 0)) == TimeBlock.AFTERNOON
    assert PlanServiceV2.get_time_block(time(20, 0)) == TimeBlock.EVENING
    assert PlanServiceV2.get_time_block(time(23, 30)) == TimeBlock.EVENING
    assert PlanServiceV2.get_time_block(time(5, 0)) == None  # Слишком рано

def test_estimate_duration():
    """Test duration estimation"""
    # Короткие задачи
    assert PlanServiceV2.estimate_duration("Позвонить маме") <= 30
    assert PlanServiceV2.estimate_duration("Выпить кофе") <= 15
    
    # Средние задачи
    assert 30 <= PlanServiceV2.estimate_duration("Подготовить презентацию") <= 120
    assert 30 <= PlanServiceV2.estimate_duration("Сходить в магазин") <= 90
    
    # Длинные задачи
    assert PlanServiceV2.estimate_duration("Написать дипломную работу") >= 180
    assert PlanServiceV2.estimate_duration("Провести исследование рынка") >= 120

@pytest.mark.asyncio
async def test_create_plan(plan_service):
    """Test plan creation"""
    plan_text = "Подготовить презентацию"
    start_time = "09:00"
    
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text=plan_text,
        start_time=start_time
    )
    
    assert plan.title == "Подготовить презентацию"
    assert plan.time_block == TimeBlock.MORNING
    assert isinstance(plan.duration_minutes, int)
    assert plan.duration_minutes > 0
    assert isinstance(plan.priority, Priority)

@pytest.mark.asyncio
async def test_check_conflicts(plan_service):
    """Test conflict checking"""
    # Создаем первый план
    plan1 = await plan_service.create_plan(
        user_id=1,
        plan_text="Встреча с клиентом",
        start_time="10:00"
    )
    
    # Проверяем конфликты
    assert await plan_service.has_conflicts(
        user_id=1,
        start_time=datetime.strptime("10:30", "%H:%M").time(),
        duration=60
    ) == True
    
    assert await plan_service.has_conflicts(
        user_id=1,
        start_time=datetime.strptime("12:00", "%H:%M").time(),
        duration=60
    ) == False

@pytest.mark.asyncio
async def test_plan_steps(plan_service):
    """Test plan steps"""
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text="""
        Подготовить презентацию
        - Собрать данные
        - Сделать слайды
        - Добавить анимацию
        """
    )
    
    assert len(plan.steps) == 3
    assert all(isinstance(step, PlanStep) for step in plan.steps)
    assert sum(step.duration_minutes for step in plan.steps) == plan.duration_minutes

@pytest.mark.asyncio
async def test_update_plan(plan_service):
    """Test plan updating"""
    # Создаем план
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text="Старый план",
        start_time="10:00"
    )
    
    # Обновляем план
    updated_plan = await plan_service.update_plan(
        plan_id=plan.id,
        new_title="Новый план",
        new_start_time="11:00"
    )
    
    assert updated_plan.title == "Новый план"
    assert updated_plan.start_time.strftime("%H:%M") == "11:00"

@pytest.mark.asyncio
async def test_delete_plan(plan_service):
    """Test plan deletion"""
    # Создаем план
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text="План на удаление",
        start_time="10:00"
    )
    
    # Удаляем план
    result = await plan_service.delete_plan(plan.id)
    assert result == True
    
    # Проверяем, что план удален
    deleted_plan = await plan_service.get_plan(plan.id)
    assert deleted_plan is None
