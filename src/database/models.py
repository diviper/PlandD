"""Database models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .db import Base

class Task(Base):
    """Task model"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    priority = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Schedule(Base):
    """Schedule model"""
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task")

class Meal(Base):
    """Meal model"""
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    calories = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReminderSettings(Base):
    """Reminder settings model"""
    __tablename__ = 'reminder_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    enabled = Column(Boolean, default=True)
    interval_minutes = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)