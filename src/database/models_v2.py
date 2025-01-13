"""Database models v2 with improved time structure"""
from datetime import datetime, time
from typing import List, Optional
import json

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
import enum

from src.database.base import Base

class TimeBlock(enum.Enum):
    """Временные блоки дня"""
    MORNING = "morning"      # 06:00-12:00
    AFTERNOON = "afternoon"  # 12:00-18:00
    EVENING = "evening"      # 18:00-23:00

class Priority(enum.Enum):
    """Приоритеты задач"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Plan(Base):
    """План пользователя с временной структурой"""
    __tablename__ = 'plans_v2'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    
    # Временная структура
    time_block = Column(Enum(TimeBlock), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Метаданные
    priority = Column(Enum(Priority), nullable=False)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deadline = Column(DateTime)

    # Связи
    steps = relationship("PlanStep", back_populates="plan", cascade="all, delete-orphan")
    progress = relationship("PlanProgress", back_populates="plan", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'time_block': self.time_block.value,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'duration_minutes': self.duration_minutes,
            'priority': self.priority.value,
            'status': self.status,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'steps': [step.to_dict() for step in self.steps]
        }

class PlanStep(Base):
    """Шаг плана с временными метриками"""
    __tablename__ = 'plan_steps_v2'

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans_v2.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    
    # Временная структура
    start_time = Column(Time)
    end_time = Column(Time)
    duration_minutes = Column(Integer)
    
    # Метаданные
    priority = Column(Enum(Priority))
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    metrics = Column(JSON)  # Критерии выполнения

    # Связи
    plan = relationship("Plan", back_populates="steps")
    progress = relationship("PlanProgress", back_populates="step", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'priority': self.priority.value if self.priority else None,
            'status': self.status,
            'metrics': self.metrics
        }

class PlanProgress(Base):
    """Прогресс выполнения плана с временными метками"""
    __tablename__ = 'plan_progress_v2'

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans_v2.id'), nullable=False)
    step_id = Column(Integer, ForeignKey('plan_steps_v2.id'), nullable=False)
    
    # Временные метки
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    actual_duration_minutes = Column(Integer)
    
    # Метаданные
    status = Column(String, nullable=False)  # started/completed/blocked
    notes = Column(String)
    blockers = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Связи
    plan = relationship("Plan", back_populates="progress")
    step = relationship("PlanStep", back_populates="progress")

    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'actual_duration_minutes': self.actual_duration_minutes,
            'notes': self.notes,
            'blockers': self.blockers
        }

class UserPreferences(Base):
    """Расширенные настройки и предпочтения пользователя"""
    __tablename__ = 'user_preferences_v2'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    
    # Временные предпочтения
    work_hours = Column(JSON)  # {"start": "09:00", "end": "18:00"}
    time_blocks = Column(JSON)  # {"morning": {"start": "06:00", "end": "12:00"}, ...}
    break_preferences = Column(JSON)  # {"duration": 15, "frequency": 120}
    
    # Приоритеты и стиль
    default_priority = Column(Enum(Priority), default=Priority.MEDIUM)
    humor_level = Column(Integer, default=20)  # процент юмора в ответах
    notification_style = Column(String, default='balanced')  # funny/serious/balanced
    
    # Аналитика
    productivity_hours = Column(JSON)  # [{"start": "10:00", "end": "12:00", "score": 0.9}, ...]
    completion_rates = Column(JSON)  # {"morning": 0.8, "afternoon": 0.7, "evening": 0.6}
    task_patterns = Column(JSON)  # {"short_tasks": 0.9, "long_tasks": 0.7}
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analysis = Column(DateTime)
    ai_confidence = Column(Float, default=0.5)  # точность AI предсказаний

    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'work_hours': self.work_hours,
            'time_blocks': self.time_blocks,
            'break_preferences': self.break_preferences,
            'default_priority': self.default_priority.value,
            'humor_level': self.humor_level,
            'notification_style': self.notification_style,
            'productivity_hours': self.productivity_hours,
            'completion_rates': self.completion_rates,
            'task_patterns': self.task_patterns,
            'ai_confidence': self.ai_confidence
        }
