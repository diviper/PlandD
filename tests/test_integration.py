"""Integration tests"""
import pytest
from datetime import datetime, timedelta
from src.services.plan_service_v2 import PlanServiceV2
from src.services.ai.ai_service import AIService
from src.services.reminder.scheduler import ReminderScheduler
from src.database.models_v2 import Plan, TimeBlock, Priority

@pytest.mark.asyncio
async def test_plan_creation_flow(plan_service, ai_service, test_user):
    """Test complete plan creation flow"""
    # 1. Analyze plan with AI
    plan_text = """
    Подготовить презентацию
    - Собрать данные
    - Сделать слайды
    - Добавить анимацию
    """
    analysis = await ai_service.analyze_plan_text(plan_text)
    
    # 2. Create plan using new format
    plan_data = {
        "title": "Подготовить презентацию",
        "description": "Создание презентации с данными и анимацией",
        "time_block": "MORNING",
        "start_time": "10:00",
        "end_time": "12:00",
        "duration_minutes": 120,
        "priority": "HIGH",
        "steps": [
            {
                "title": "Собрать данные",
                "description": "Сбор необходимых данных для презентации",
                "duration_minutes": 40
            },
            {
                "title": "Сделать слайды",
                "description": "Создание слайдов презентации",
                "duration_minutes": 50
            },
            {
                "title": "Добавить анимацию",
                "description": "Добавление анимационных эффектов",
                "duration_minutes": 30
            }
        ]
    }
    
    plan = await plan_service.create_plan(test_user.id, plan_data)
    
    # 3. Verify plan
    assert plan.title == "Подготовить презентацию"
    assert len(plan.steps) == 3
    assert plan.time_block == TimeBlock.MORNING
    assert plan.priority == Priority.HIGH

@pytest.mark.asyncio
async def test_reminder_flow(plan_service, bot, db, test_user):
    """Test reminder scheduling flow"""
    # 1. Create plan
    next_time = (datetime.now() + timedelta(minutes=5)).strftime("%H:%M")
    end_time = (datetime.now() + timedelta(minutes=35)).strftime("%H:%M")
    
    plan_data = {
        "title": "Важная встреча",
        "description": "Срочная встреча с командой",
        "time_block": "MORNING",
        "start_time": next_time,
        "end_time": end_time,
        "duration_minutes": 30,
        "priority": "HIGH"
    }
    
    plan = await plan_service.create_plan(test_user.id, plan_data)
    
    # 2. Schedule reminder
    scheduler = ReminderScheduler(bot, db)
    job = await scheduler.schedule_reminder(plan)
    
    # 3. Verify reminder
    assert job is not None
    assert job.next_run_time is not None
    
    # 4. Clean up
    scheduler.scheduler.remove_job(job.id)

@pytest.mark.asyncio
async def test_plan_update_flow(plan_service, ai_service, test_user):
    """Test plan update flow"""
    # 1. Create initial plan
    initial_plan_data = {
        "title": "Первоначальный план",
        "description": "Описание первоначального плана",
        "time_block": "MORNING",
        "start_time": "10:00",
        "end_time": "11:00",
        "duration_minutes": 60,
        "priority": "MEDIUM"
    }
    
    plan = await plan_service.create_plan(test_user.id, initial_plan_data)
    
    # 2. Update plan
    update_data = {
        "title": "Обновленный план",
        "start_time": "11:00",
        "end_time": "12:00",
        "priority": "HIGH"
    }
    
    updated_plan = await plan_service.update_plan(plan.id, update_data)
    
    # 3. Verify updates
    assert updated_plan.title == "Обновленный план"
    assert updated_plan.priority == Priority.HIGH
    assert updated_plan.start_time.strftime("%H:%M") == "11:00"

@pytest.mark.asyncio
async def test_multiple_plans_handling(plan_service, test_user):
    """Test handling of multiple plans"""
    # 1. Create multiple plans
    plans = []
    for i in range(3):
        plan_data = {
            "title": f"План {i+1}",
            "description": f"Описание плана {i+1}",
            "time_block": "MORNING",
            "start_time": f"{10+i}:00",
            "end_time": f"{11+i}:00",
            "duration_minutes": 60,
            "priority": "MEDIUM"
        }
        plan = await plan_service.create_plan(test_user.id, plan_data)
        plans.append(plan)
    
    # 2. Get user's plans
    user_plans = await plan_service.get_user_plans(test_user.id)
    
    # 3. Verify plans
    assert len(user_plans) == 3
    assert all(isinstance(p, Plan) for p in user_plans)
    assert all(p.user_id == test_user.id for p in user_plans)

@pytest.mark.asyncio
async def test_plan_deletion_flow(plan_service, bot, db, test_user):
    """Test plan deletion flow"""
    # 1. Create plan
    plan_data = {
        "title": "План для удаления",
        "description": "Этот план будет удален",
        "time_block": "MORNING",
        "start_time": "10:00",
        "end_time": "11:00",
        "duration_minutes": 60,
        "priority": "LOW"
    }
    
    plan = await plan_service.create_plan(test_user.id, plan_data)
    
    # 2. Schedule reminder
    scheduler = ReminderScheduler(bot, db)
    job = await scheduler.schedule_reminder(plan)
    
    # 3. Delete plan
    await plan_service.delete_plan(plan.id)
    
    # 4. Verify deletion
    user_plans = await plan_service.get_user_plans(test_user.id)
    assert plan.id not in [p.id for p in user_plans]
    
    # 5. Verify reminder cleanup
    assert scheduler.scheduler.get_job(str(plan.id)) is None

@pytest.mark.asyncio
async def test_ai_integration(ai_service, plan_service, test_user):
    """Test AI service integration"""
    # 1. Get AI analysis
    plan_text = """
    Важная презентация!!!
    - Подготовить данные
    - Создать слайды
    - Добавить эффекты
    """
    
    analysis = await ai_service.analyze_plan_text(plan_text)
    
    # 2. Create plan from analysis
    plan_data = {
        "title": analysis["title"],
        "description": "План, созданный на основе AI анализа",
        "time_block": analysis.get("time_block", "MORNING"),
        "start_time": "10:00",
        "end_time": "12:00",
        "duration_minutes": sum(int(step.get("duration", 30)) for step in analysis.get("steps", [])),
        "priority": analysis.get("priority", "HIGH"),
        "steps": [
            {
                "title": step["description"],
                "description": step.get("rick_comment", ""),
                "duration_minutes": int(step["duration"])
            }
            for step in analysis.get("steps", [])
        ]
    }
    
    plan = await plan_service.create_plan(test_user.id, plan_data)
    
    # 3. Verify AI integration
    assert plan.title == analysis["title"]
    assert len(plan.steps) == len(analysis.get("steps", []))
    assert isinstance(plan.priority, Priority)
