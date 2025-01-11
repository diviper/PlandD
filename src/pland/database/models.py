"""Models module for PlanD database"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class Task(Base):
    """Task model representing a user's task"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    priority = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)
    parent_task_id = Column(Integer, ForeignKey('tasks.id'))
    estimated_duration = Column(Integer)  # В минутах
    energy_level = Column(Integer)  # От 1 до 10
    energy_type = Column(String)  # mental/physical/emotional
    optimal_time = Column(String)  # morning/afternoon/evening
    category = Column(String)
    focus_required = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Исправленная связь для подзадач
    subtasks = relationship("Task",
                         backref="parent",
                         remote_side=[id],
                         cascade="all, delete")

class Schedule(Base):
    """Schedule model representing a user's daily schedule"""
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    sleep_time = Column(String)
    wake_time = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Meal(Base):
    """Meal model representing a user's meal schedule"""
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    meal_time = Column(String, nullable=False)
    meal_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReminderSettings(Base):
    """Model for user's reminder preferences"""
    __tablename__ = 'reminder_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    default_reminder_time = Column(Integer, default=30)  # Minutes before task
    morning_reminder_time = Column(String, default="09:00")  # Daily morning summary time
    evening_reminder_time = Column(String, default="20:00")  # Daily evening summary time
    priority_high_interval = Column(Integer, default=30)  # Minutes between high priority reminders
    priority_medium_interval = Column(Integer, default=60)  # Minutes between medium priority reminders
    priority_low_interval = Column(Integer, default=120)  # Minutes between low priority reminders
    quiet_hours_start = Column(String, default="23:00")  # Start of quiet hours
    quiet_hours_end = Column(String, default="07:00")  # End of quiet hours
    reminder_types = Column(String, default="all")  # Types of reminders to receive ('all' or specific types)

    def get_reminder_types(self) -> List[str]:
        """Get reminder types as list"""
        if not self.reminder_types:
            return ["all"]
        return self.reminder_types.split(',')

    def set_reminder_types(self, types: List[str]):
        """Set reminder types from list"""
        self.reminder_types = ','.join(types) if types else "all"