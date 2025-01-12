"""Database module for PlanD"""
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict
import asyncio

from sqlalchemy import create_engine, select, or_, and_
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Config

logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
Base = declarative_base()

class Database:
    """Database handler class"""
    def __init__(self):
        """Initialize database"""
        logger.info(f"Initializing database: {Config.DATABASE_PATH}")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
        
        # Create engine and session factory
        self.engine = create_engine(f'sqlite:///{Config.DATABASE_PATH}')
        self.session_factory = sessionmaker(bind=self.engine)
        self._lock = asyncio.Lock()
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")

    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()

    async def add_task(self, task: Task) -> int:
        """Add a new task to the database"""
        async with self._lock:
            session = self.get_session()
            try:
                session.add(task)
                session.commit()
                task_id = task.id
                logger.debug(f"Added task with ID: {task_id}")
                return task_id
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding task: {str(e)}")
                raise
            finally:
                session.close()

    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID"""
        async with self._lock:
            session = self.get_session()
            try:
                task = session.get(Task, task_id)
                return task
            finally:
                session.close()

    async def get_user_tasks(self, user_id: int, include_completed: bool = False) -> List[Task]:
        """Get all tasks for a specific user"""
        async with self._lock:
            session = self.get_session()
            try:
                query = select(Task).where(Task.user_id == user_id)
                if not include_completed:
                    query = query.where(Task.completed == False)
                tasks = session.execute(query).scalars().all()
                return list(tasks)
            finally:
                session.close()

    async def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task fields"""
        async with self._lock:
            session = self.get_session()
            try:
                task = session.get(Task, task_id)
                if not task:
                    return False
                
                for key, value in kwargs.items():
                    setattr(task, key, value)
                
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating task {task_id}: {str(e)}")
                return False
            finally:
                session.close()

    async def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        async with self._lock:
            session = self.get_session()
            try:
                task = session.get(Task, task_id)
                if not task:
                    return False
                
                session.delete(task)
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error deleting task {task_id}: {str(e)}")
                return False
            finally:
                session.close()

    async def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        async with self._lock:
            session = self.get_session()
            try:
                query = select(UserPreferences).where(UserPreferences.user_id == user_id)
                result = session.execute(query).scalar_one_or_none()
                return result
            finally:
                session.close()

    async def update_user_preferences(self, user_id: int, **kwargs) -> bool:
        """Update user preferences"""
        async with self._lock:
            session = self.get_session()
            try:
                prefs = session.execute(
                    select(UserPreferences).where(UserPreferences.user_id == user_id)
                ).scalar_one_or_none()

                if not prefs:
                    prefs = UserPreferences(user_id=user_id)
                    session.add(prefs)

                for key, value in kwargs.items():
                    setattr(prefs, key, value)

                prefs.updated_at = datetime.utcnow()
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating preferences for user {user_id}: {str(e)}")
                return False
            finally:
                session.close()

    async def get_reminder_settings(self, user_id: int) -> Optional[ReminderSettings]:
        """Get reminder settings for a user"""
        async with self._lock:
            session = self.get_session()
            try:
                query = select(ReminderSettings).where(ReminderSettings.user_id == user_id)
                result = session.execute(query).scalar_one_or_none()
                return result
            finally:
                session.close()

    async def update_reminder_settings(self, user_id: int, **kwargs) -> bool:
        """Update reminder settings"""
        async with self._lock:
            session = self.get_session()
            try:
                settings = session.execute(
                    select(ReminderSettings).where(ReminderSettings.user_id == user_id)
                ).scalar_one_or_none()

                if not settings:
                    settings = ReminderSettings(user_id=user_id)
                    session.add(settings)

                for key, value in kwargs.items():
                    setattr(settings, key, value)

                settings.updated_at = datetime.utcnow()
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating reminder settings for user {user_id}: {str(e)}")
                return False
            finally:
                session.close()

    async def add_plan(self, plan_data: Dict) -> int:
        """Add a new plan to the database"""
        from .models import Plan, PlanStep  # Import here to avoid circular imports
        
        async with self._lock:
            session = self.get_session()
            try:
                # Create plan
                plan = Plan(
                    user_id=plan_data['user_id'],
                    type=plan_data['type'],
                    title=plan_data['title'],
                    description=plan_data.get('description'),
                    estimated_duration=plan_data['estimated_duration'],
                    priority=plan_data['priority']
                )
                session.add(plan)
                session.flush()  # Get plan ID

                # Create steps
                for step_data in plan_data.get('steps', []):
                    step = PlanStep(
                        plan_id=plan.id,
                        title=step_data['title'],
                        description=step_data.get('description'),
                        duration=step_data['duration'],
                        prerequisites=step_data.get('prerequisites'),
                        metrics=step_data.get('metrics')
                    )
                    session.add(step)

                session.commit()
                logger.info(f"Added plan with ID: {plan.id}")
                return plan.id
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding plan: {str(e)}")
                raise
            finally:
                session.close()

    async def get_plan(self, plan_id: int) -> Optional[Dict]:
        """Get a plan by ID with all its steps"""
        from .models import Plan, PlanStep  # Import here to avoid circular imports
        
        async with self._lock:
            session = self.get_session()
            try:
                # Get plan with steps
                stmt = select(Plan).where(Plan.id == plan_id)
                plan = session.execute(stmt).scalar_one_or_none()
                
                if not plan:
                    return None
                
                # Get steps
                stmt = select(PlanStep).where(PlanStep.plan_id == plan_id)
                steps = session.execute(stmt).scalars().all()
                
                # Convert to dict
                return {
                    'id': plan.id,
                    'user_id': plan.user_id,
                    'type': plan.type,
                    'title': plan.title,
                    'description': plan.description,
                    'estimated_duration': plan.estimated_duration,
                    'priority': plan.priority,
                    'status': plan.status,
                    'created_at': plan.created_at.isoformat(),
                    'steps': [
                        {
                            'id': step.id,
                            'title': step.title,
                            'description': step.description,
                            'duration': step.duration,
                            'prerequisites': step.prerequisites,
                            'metrics': step.metrics,
                            'status': step.status
                        }
                        for step in steps
                    ]
                }
            except Exception as e:
                logger.error(f"Error getting plan: {str(e)}")
                raise
            finally:
                session.close()

    async def update_plan_progress(self, plan_id: int, step_id: int, status: str, notes: str = None) -> bool:
        """Update plan step progress"""
        from .models import PlanProgress  # Import here to avoid circular imports
        
        async with self._lock:
            session = self.get_session()
            try:
                progress = PlanProgress(
                    plan_id=plan_id,
                    step_id=step_id,
                    status=status,
                    notes=notes
                )
                session.add(progress)
                session.commit()
                logger.info(f"Updated progress for plan {plan_id}, step {step_id}")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating progress: {str(e)}")
                return False
            finally:
                session.close()