"""Database module for PlanD"""
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from src.core.config import Config
from .db import Session as DBSession, init_db
from .models import Task, Schedule, Meal, ReminderSettings

logger = logging.getLogger(__name__)

class Database:
    """Database handler class"""
    def __init__(self):
        """Initialize database"""
        logger.info(f"Initializing database: {Config.DATABASE_PATH}")
        init_db()  # Initialize database and create tables if they don't exist
        self.session_factory = DBSession

    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()

    def add_task(self, task: Task) -> int:
        """Add a new task to the database"""
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

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID"""
        session = self.get_session()
        try:
            task = session.get(Task, task_id)
            return task
        finally:
            session.close()

    def get_tasks(self, user_id: int) -> List[Task]:
        """Get all tasks for a specific user"""
        session = self.get_session()
        try:
            tasks = session.execute(
                select(Task).where(Task.user_id == user_id)
            ).scalars().all()
            return tasks
        finally:
            session.close()

    def update_reminder_settings(self, settings: ReminderSettings) -> bool:
        """Update or create reminder settings for a user"""
        session = self.get_session()
        try:
            existing = session.execute(
                select(ReminderSettings).where(
                    ReminderSettings.user_id == settings.user_id
                )
            ).scalar_one_or_none()

            if existing:
                # Update existing settings
                for column in ReminderSettings.__table__.columns:
                    if column.name != 'id':
                        setattr(existing, column.name, getattr(settings, column.name))
            else:
                # Add new settings
                session.add(settings)

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating reminder settings: {str(e)}")
            return False
        finally:
            session.close()

    def get_reminder_settings(self, user_id: int) -> Optional[ReminderSettings]:
        """Get reminder settings for a user"""
        session = self.get_session()
        try:
            settings = session.execute(
                select(ReminderSettings).where(
                    ReminderSettings.user_id == user_id
                )
            ).scalar_one_or_none()
            return settings
        finally:
            session.close()

    def get_upcoming_tasks(self, user_id: int) -> List[Task]:
        """Get upcoming tasks for a specific user"""
        session = self.get_session()
        try:
            current_time = datetime.utcnow()
            tasks = session.execute(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.due_date > current_time,
                    Task.completed == False
                ).order_by(Task.due_date)
            ).scalars().all()
            return tasks
        finally:
            session.close()

    def update_task_status(self, task_id: int, completed: bool):
        """Update task completion status"""
        session = self.get_session()
        try:
            task = session.get(Task, task_id)
            if task:
                task.completed = completed
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating task status: {str(e)}")
            raise
        finally:
            session.close()

    def delete_task(self, task_id: int):
        """Delete a task by ID"""
        session = self.get_session()
        try:
            task = session.get(Task, task_id)
            if task:
                session.delete(task)
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting task: {str(e)}")
            raise
        finally:
            session.close()

    def update_schedule(self, schedule: Schedule):
        """Update or create a user's schedule"""
        session = self.get_session()
        try:
            existing = session.execute(
                select(Schedule).where(Schedule.user_id == schedule.user_id)
            ).scalar_one_or_none()

            if existing:
                existing.sleep_time = schedule.sleep_time
                existing.wake_time = schedule.wake_time
            else:
                session.add(schedule)

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating schedule: {str(e)}")
            raise
        finally:
            session.close()

    def add_meal(self, meal: Meal):
        """Add a new meal schedule"""
        session = self.get_session()
        try:
            session.add(meal)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding meal: {str(e)}")
            raise
        finally:
            session.close()

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from the database"""
        session = self.get_session()
        try:
            tasks = session.execute(select(Task)).scalars().all()
            return tasks
        finally:
            session.close()