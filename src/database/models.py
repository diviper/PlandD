"""Database models for PlanD"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship

from .database import Base

class Plan(Base):
    """План пользователя"""
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # personal/work/study/health
    title = Column(String, nullable=False)
    description = Column(String)
    estimated_duration = Column(Integer)  # в днях
    priority = Column(String, nullable=False)
    status = Column(String, default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    steps = relationship("PlanStep", back_populates="plan")
    progress = relationship("PlanProgress", back_populates="plan")

class PlanStep(Base):
    """Шаг плана"""
    __tablename__ = 'plan_steps'

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer)  # в днях
    prerequisites = Column(JSON)  # ID предыдущих шагов
    metrics = Column(JSON)  # Критерии выполнения
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="steps")
    progress = relationship("PlanProgress", back_populates="step")

class PlanProgress(Base):
    """Прогресс выполнения плана"""
    __tablename__ = 'plan_progress'

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    step_id = Column(Integer, ForeignKey('plan_steps.id'), nullable=False)
    status = Column(String, nullable=False)  # started/completed/blocked
    notes = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="progress")
    step = relationship("PlanStep", back_populates="progress")

class UserPreferences(Base):
    """Настройки и предпочтения пользователя"""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    
    # Рабочие предпочтения
    preferred_work_hours = Column(JSON)  # {"start": "09:00", "end": "18:00"}
    peak_productivity_hours = Column(JSON)  # [{"start": "10:00", "end": "12:00"}, ...]
    preferred_break_duration = Column(Integer, default=15)  # минуты
    
    # Аналитика
    avg_task_completion_rate = Column(Float)  # процент выполнения в срок
    typical_energy_curve = Column(JSON)  # {"morning": 8, "afternoon": 6, ...}
    common_distractions = Column(JSON)  # ["meetings", "emails", ...]
    task_success_patterns = Column(JSON)  # {"short_tasks": 0.9, "long_tasks": 0.7}
    productivity_factors = Column(JSON)  # {"sleep": 0.8, "exercise": 0.6}
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analysis = Column(DateTime)
    confidence_score = Column(Float, default=0.5)  # точность предсказаний