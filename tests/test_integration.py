"""Integration tests"""
import pytest
from datetime import datetime, timedelta
from src.services.plan_service_v2 import PlanServiceV2
from src.services.ai.ai_service import AIService
from src.services.reminder.scheduler import ReminderScheduler
from src.database.models_v2 import Plan, TimeBlock, Priority

@pytest.mark.asyncio
async def test_plan_creation_flow(plan_service, ai_service):
    """Test complete plan creation flow"""
    # 1. Analyze plan with AI
    plan_text = """
    Подготовить презентацию
    - Собрать данные
    - Сделать слайды
    - Добавить анимацию
    """
    analysis = await ai_service.analyze_plan(plan_text)
    
    # 2. Create plan
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text=plan_text,
        start_time="10:00"
    )
    
    # 3. Verify plan
    assert plan.title == "Подготовить презентацию"
    assert len(plan.steps) == 3
    assert plan.time_block == TimeBlock.MORNING
    assert isinstance(plan.priority, Priority)

@pytest.mark.asyncio
async def test_reminder_flow(plan_service, bot, db):
    """Test reminder scheduling flow"""
    # 1. Create plan
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text="Важная встреча",
        start_time=(datetime.now() + timedelta(minutes=5)).strftime("%H:%M")
    )
    
    # 2. Schedule reminder
    scheduler = ReminderScheduler(bot, db)
    job = await scheduler.schedule_reminder(plan)
    
    # 3. Verify reminder
    assert job is not None
    assert job.next_run_time is not None
    
    # 4. Clean up
    scheduler.scheduler.remove_job(job.id)

@pytest.mark.asyncio
async def test_plan_update_flow(plan_service, ai_service):
    """Test plan update flow"""
    # 1. Create initial plan
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text="Первоначальный план",
        start_time="10:00"
    )
    
    # 2. Update plan
    new_text = "Обновленный план"
    analysis = await ai_service.analyze_plan(new_text)
    
    updated_plan = await plan_service.update_plan(
        plan_id=plan.id,
        new_title=new_text,
        new_start_time="11:00"
    )
    
    # 3. Verify updates
    assert updated_plan.title == new_text
    assert updated_plan.start_time.strftime("%H:%M") == "11:00"

@pytest.mark.asyncio
async def test_multiple_plans_handling(plan_service):
    """Test handling of multiple plans"""
    # 1. Create multiple plans
    plans = []
    for i in range(3):
        plan = await plan_service.create_plan(
            user_id=1,
            plan_text=f"План {i+1}",
            start_time=f"{10+i}:00"
        )
        plans.append(plan)
    
    # 2. Get user's plans
    user_plans = await plan_service.get_user_plans(1)
    
    # 3. Verify plans
    assert len(user_plans) == 3
    assert all(isinstance(p, Plan) for p in user_plans)
    assert all(p.user_id == 1 for p in user_plans)

@pytest.mark.asyncio
async def test_plan_deletion_flow(plan_service, bot, db):
    """Test plan deletion flow"""
    # 1. Create plan with reminder
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text="План на удаление",
        start_time="12:00"
    )
    
    scheduler = ReminderScheduler(bot, db)
    job = await scheduler.schedule_reminder(plan)
    
    # 2. Delete plan
    success = await plan_service.delete_plan(plan.id)
    assert success
    
    # 3. Verify plan is deleted
    deleted_plan = await plan_service.get_plan(plan.id)
    assert deleted_plan is None
    
    # 4. Verify reminder is removed
    assert scheduler.scheduler.get_job(str(plan.id)) is None

@pytest.mark.asyncio
async def test_ai_integration(ai_service, plan_service):
    """Test AI service integration"""
    # 1. Complex plan analysis
    plan_text = """
    Важная презентация!!!
    - Подготовить данные
    - Создать слайды
    - Провести репетицию
    """
    
    # 2. AI Analysis
    analysis = await ai_service.analyze_plan(plan_text)
    assert "priority" in analysis
    assert analysis["priority"] == Priority.HIGH
    
    # 3. Create plan using analysis
    plan = await plan_service.create_plan(
        user_id=1,
        plan_text=plan_text,
        start_time="14:00"
    )
    
    # 4. Verify AI-enhanced plan
    assert plan.priority == Priority.HIGH
    assert len(plan.steps) == 3
    assert all(step.duration_minutes > 0 for step in plan.steps)
