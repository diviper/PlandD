"""Service for handling plans with time structure"""
from datetime import datetime, time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.database.models_v2 import Plan, PlanStep, PlanProgress, UserPreferences, TimeBlock, Priority

class PlanServiceV2:
    def __init__(self, db: Session):
        self.db = db

    def create_plan(self, user_id: int, data: Dict[str, Any]) -> Plan:
        """Create a new plan with time structure"""
        plan = Plan(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            time_block=TimeBlock[data['time_block'].upper()],
            start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
            duration_minutes=data['duration_minutes'],
            priority=Priority[data['priority'].upper()],
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None
        )
        
        # Добавляем шаги плана
        if 'steps' in data:
            for step_data in data['steps']:
                step = PlanStep(
                    title=step_data['title'],
                    description=step_data.get('description'),
                    start_time=datetime.strptime(step_data['start_time'], '%H:%M').time() if step_data.get('start_time') else None,
                    end_time=datetime.strptime(step_data['end_time'], '%H:%M').time() if step_data.get('end_time') else None,
                    duration_minutes=step_data.get('duration_minutes'),
                    priority=Priority[step_data['priority'].upper()] if step_data.get('priority') else None,
                    metrics=step_data.get('metrics', {})
                )
                plan.steps.append(step)
        
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def get_user_plans(self, user_id: int, time_block: Optional[str] = None, 
                      priority: Optional[str] = None, status: Optional[str] = None) -> List[Plan]:
        """Get user plans with optional filters"""
        query = self.db.query(Plan).filter(Plan.user_id == user_id)
        
        if time_block:
            query = query.filter(Plan.time_block == TimeBlock[time_block.upper()])
        if priority:
            query = query.filter(Plan.priority == Priority[priority.upper()])
        if status:
            query = query.filter(Plan.status == status)
            
        return query.order_by(Plan.start_time).all()

    def update_plan_status(self, plan_id: int, status: str) -> Plan:
        """Update plan status"""
        plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
            
        plan.status = status
        plan.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def add_plan_progress(self, plan_id: int, step_id: int, data: Dict[str, Any]) -> PlanProgress:
        """Add progress update for a plan step"""
        progress = PlanProgress(
            plan_id=plan_id,
            step_id=step_id,
            status=data['status'],
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            actual_duration_minutes=data.get('actual_duration_minutes'),
            notes=data.get('notes'),
            blockers=data.get('blockers', {})
        )
        
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        return self.db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()

    def update_user_preferences(self, user_id: int, data: Dict[str, Any]) -> UserPreferences:
        """Update user preferences"""
        prefs = self.db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
        
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            self.db.add(prefs)
        
        # Обновляем только предоставленные поля
        for key, value in data.items():
            if hasattr(prefs, key):
                if key == 'default_priority' and value:
                    value = Priority[value.upper()]
                setattr(prefs, key, value)
        
        prefs.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(prefs)
        return prefs

    def format_plan_for_display(self, plan: Plan) -> str:
        """Format plan for display in Telegram message"""
        result = [
            f"⏰ {plan.start_time.strftime('%H:%M')}-{plan.end_time.strftime('%H:%M')} | {plan.title}",
            f"📝 {plan.description}" if plan.description else "",
            f"🎯 Приоритет: {plan.priority.value.capitalize()}",
            f"⏱ Длительность: {plan.duration_minutes} минут",
            f"📅 Дедлайн: {plan.deadline.strftime('%Y-%m-%d %H:%M')}" if plan.deadline else "",
            "\nШаги:",
        ]
        
        for step in plan.steps:
            step_time = f"{step.start_time.strftime('%H:%M')}-{step.end_time.strftime('%H:%M')}" if step.start_time and step.end_time else "⏰ Время не указано"
            result.extend([
                f"\n{step_time}",
                f"- {step.title}",
                f"  {step.description}" if step.description else "",
                f"  ⏱ {step.duration_minutes} минут" if step.duration_minutes else ""
            ])
        
        return "\n".join(line for line in result if line)
