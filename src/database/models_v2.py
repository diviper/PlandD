"""Database models v2 with improved time structure"""
from datetime import datetime, time
from typing import List, Optional
import json

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, ForeignKey, JSON, Float, Enum, MetaData
from sqlalchemy.orm import relationship, declarative_base
import enum

# Создаем отдельный MetaData для наших моделей
metadata = MetaData()
Base = declarative_base(metadata=metadata)

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

class User(Base):
    """Пользователь системы"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    plans = relationship("Plan", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

class Plan(Base):
    """План пользователя с временной структурой"""
    __tablename__ = 'plans_v2'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
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
    user = relationship("User", back_populates="plans")
    steps = relationship("PlanStep", back_populates="plan", cascade="all, delete-orphan")
    progress = relationship("PlanProgress", back_populates="plan", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'time_block': self.time_block.value,
            'start_time': self.start_time.strftime("%H:%M") if self.start_time else None,
            'end_time': self.end_time.strftime("%H:%M") if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'priority': self.priority.value,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'steps': [step.to_dict() for step in self.steps],
            'progress': [prog.to_dict() for prog in self.progress]
        }

class PlanStep(Base):
    """Шаг плана с временными метриками"""
    __tablename__ = 'plan_steps_v2'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans_v2.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    order = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(String, default='pending')
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Связи
    plan = relationship("Plan", back_populates="steps")
    
    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class PlanProgress(Base):
    """Прогресс выполнения плана с временными метками"""
    __tablename__ = 'plan_progress_v2'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans_v2.id'), nullable=False)
    step_id = Column(Integer, ForeignKey('plan_steps_v2.id'))
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    note = Column(String)
    metrics = Column(JSON)
    
    # Связи
    plan = relationship("Plan", back_populates="progress")
    
    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'step_id': self.step_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'note': self.note,
            'metrics': self.metrics
        }

class UserPreferences(Base):
    """Расширенные настройки и предпочтения пользователя"""
    __tablename__ = 'user_preferences_v2'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    work_hours = Column(JSON)
    time_blocks = Column(JSON)
    break_preferences = Column(JSON)
    default_priority = Column(Enum(Priority), default=Priority.MEDIUM)
    humor_level = Column(Integer, default=20)
    notification_style = Column(String, default='balanced')
    productivity_hours = Column(JSON)
    completion_rates = Column(JSON)
    task_patterns = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analysis = Column(DateTime)
    ai_confidence = Column(Float, default=0.5)

    # Связи
    user = relationship("User", back_populates="preferences")

    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'work_hours': self.work_hours,
            'time_blocks': self.time_blocks,
            'break_preferences': self.break_preferences,
            'default_priority': self.default_priority.value if self.default_priority else None,
            'humor_level': self.humor_level,
            'notification_style': self.notification_style,
            'productivity_hours': self.productivity_hours,
            'completion_rates': self.completion_rates,
            'task_patterns': self.task_patterns,
            'ai_confidence': self.ai_confidence
        }

class UserProfile(Base):
    """Профиль пользователя"""
    __tablename__ = 'user_profiles'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    coins = Column(Integer, default=0)
    interaction_style = Column(String, default='rick')
    premium_until = Column(DateTime)
    settings = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    user = relationship("User", back_populates="profile")

    def to_dict(self) -> dict:
        """Конвертация в словарь для API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'coins': self.coins,
            'interaction_style': self.interaction_style,
            'premium_until': self.premium_until.isoformat() if self.premium_until else None,
            'settings': self.settings
        }
