"""Plan Service V2 with improved time management"""
from datetime import datetime, time
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models_v2 import Plan, User, TimeBlock, Priority, PlanStep
from src.core.exceptions import (
    InvalidTimeFormatError,
    TimeConflictError,
    PlanNotFoundError,
    InvalidPriorityError,
    InvalidTimeBlockError,
    EmptyPlanError,
    PastTimeError,
    InvalidUserError,
    PlanTooLongError
)

class PlanServiceV2:
    """Service for managing plans with improved time management"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_plan(self, plan_id: int) -> Plan:
        """Get plan by ID"""
        stmt = select(Plan).where(Plan.id == plan_id).options(
            selectinload(Plan.steps),
            selectinload(Plan.progress)
        )
        result = await self.session.execute(stmt)
        plan = result.scalar_one_or_none()
        
        if not plan:
            raise PlanNotFoundError(f"Plan with ID {plan_id} not found")
        
        return plan
    
    async def get_user_plans(
        self,
        user_id: int,
        time_block: Optional[str] = None,
        priority: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Plan]:
        """Get user plans with optional filters"""
        stmt = select(Plan).where(Plan.user_id == user_id)
        
        if time_block:
            stmt = stmt.where(Plan.time_block == TimeBlock(time_block))
        if priority:
            stmt = stmt.where(Plan.priority == Priority(priority))
        if start_date:
            stmt = stmt.where(Plan.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Plan.created_at <= end_date)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create_plan(self, user_id: int, plan_data: Dict[str, Any]) -> Plan:
        """Create a new plan"""
        # Проверяем пользователя
        user_stmt = select(User).where(User.id == user_id)
        user = await self.session.execute(user_stmt)
        if not user.scalar_one_or_none():
            raise InvalidUserError(f"User with ID {user_id} not found")
        
        # Валидация данных
        if not plan_data.get("title"):
            raise EmptyPlanError("Plan title cannot be empty")
            
        # Проверяем формат времени
        start_time = await self.validate_time(plan_data["start_time"])
        end_time = await self.validate_time(plan_data["end_time"])
        
        # Проверяем, что время не в прошлом
        now = datetime.now().time()
        if start_time < now:
            raise PastTimeError("Cannot create plan with past time")
        
        # Проверяем конфликты
        if await self.check_conflicts(user_id, start_time, end_time):
            raise TimeConflictError("Time conflict with existing plan")
        
        # Создаем план
        plan = Plan(
            user_id=user_id,
            title=plan_data["title"],
            description=plan_data.get("description", ""),
            time_block=TimeBlock(plan_data["time_block"]),
            start_time=start_time,
            end_time=end_time,
            duration_minutes=plan_data["duration_minutes"],
            priority=Priority(plan_data["priority"])
        )
        
        # Добавляем шаги, если есть
        if "steps" in plan_data:
            for step_data in plan_data["steps"]:
                step = PlanStep(
                    title=step_data["title"],
                    description=step_data.get("description", ""),
                    order=step_data["order"],
                    duration_minutes=step_data["duration_minutes"]
                )
                plan.steps.append(step)
        
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        
        return plan
    
    async def update_plan(self, plan_id: int, update_data: Dict[str, Any]) -> Plan:
        """Update existing plan"""
        plan = await self.get_plan(plan_id)
        
        for key, value in update_data.items():
            if key == "time_block":
                plan.time_block = TimeBlock(value)
            elif key == "priority":
                plan.priority = Priority(value)
            elif key == "start_time":
                plan.start_time = await self.validate_time(value)
            elif key == "end_time":
                plan.end_time = await self.validate_time(value)
            elif hasattr(plan, key):
                setattr(plan, key, value)
        
        await self.session.commit()
        await self.session.refresh(plan)
        
        return plan
    
    async def delete_plan(self, plan_id: int) -> None:
        """Delete plan"""
        plan = await self.get_plan(plan_id)
        await self.session.delete(plan)
        await self.session.commit()
    
    async def validate_time(self, time_str: str) -> time:
        """Validate time string and convert to time object"""
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            raise InvalidTimeFormatError(f"Invalid time format: {time_str}. Use HH:MM format")
    
    async def get_time_block(self, time_str: str) -> TimeBlock:
        """Get time block for given time"""
        t = await self.validate_time(time_str)
        hour = t.hour
        
        if 6 <= hour < 12:
            return TimeBlock.MORNING
        elif 12 <= hour < 18:
            return TimeBlock.AFTERNOON
        elif 18 <= hour < 23:
            return TimeBlock.EVENING
        else:
            raise InvalidTimeBlockError(f"No time block available for {time_str}")
    
    async def estimate_duration(self, plan_data: Dict[str, Any]) -> int:
        """Estimate plan duration in minutes"""
        if "steps" in plan_data:
            return sum(step["duration_minutes"] for step in plan_data["steps"])
        else:
            return 60  # Значение по умолчанию
    
    async def check_conflicts(self, user_id: int, start_time: time, end_time: time) -> bool:
        """Check for time conflicts with existing plans"""
        stmt = select(Plan).where(
            Plan.user_id == user_id,
            Plan.start_time <= end_time,
            Plan.end_time >= start_time
        )
        result = await self.session.execute(stmt)
        return bool(result.first())
    
    async def update_plan_step(self, plan_id: int, step_id: int, update_data: Dict[str, Any]) -> Plan:
        """Update plan step"""
        plan = await self.get_plan(plan_id)
        step = next((s for s in plan.steps if s.id == step_id), None)
        
        if not step:
            raise ValueError(f"Step {step_id} not found in plan {plan_id}")
        
        for key, value in update_data.items():
            if hasattr(step, key):
                setattr(step, key, value)
        
        await self.session.commit()
        await self.session.refresh(plan)
        
        return plan
    
    async def delete_plan_step(self, plan_id: int, step_id: int) -> Plan:
        """Delete plan step"""
        plan = await self.get_plan(plan_id)
        step = next((s for s in plan.steps if s.id == step_id), None)
        
        if not step:
            raise ValueError(f"Step {step_id} not found in plan {plan_id}")
        
        plan.steps.remove(step)
        await self.session.commit()
        await self.session.refresh(plan)
        
        return plan
