"""Database models"""
from datetime import datetime
from typing import List, Optional
import json
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Float, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from src.database.base import Base

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
    calendar_event_id = Column(Integer, ForeignKey('calendar_events.id'), nullable=True)
    is_flexible = Column(Boolean, default=True)
    reminder_times = Column(JSON)
    completion_reward = Column(Integer, default=10)

    steps = relationship("PlanStep", back_populates="plan")
    progress = relationship("PlanProgress", back_populates="plan")
    calendar_event = relationship("CalendarEvent")

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
    completion_reward = Column(Integer, default=5)

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

class InteractionStyle(Enum):
    """Стили взаимодействия бота"""
    RICK = "rick"          # Стиль Рика (базовый)
    STRICT = "strict"      # Строгий стиль
    MINIMAL = "minimal"    # Минималистичный
    FRIENDLY = "friendly"  # Дружелюбный
    ANIME = "anime"       # Аниме-стиль
    CUSTOM = "custom"     # Пользовательский стиль

class CalendarType(Enum):
    """Типы поддерживаемых календарей"""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    APPLE = "apple"
    CUSTOM = "custom"

class UserProfile(Base):
    """Расширенный профиль пользователя"""
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    coins = Column(Integer, default=0)
    interaction_style = Column(SQLAlchemyEnum(InteractionStyle), default=InteractionStyle.RICK)
    premium_until = Column(DateTime, nullable=True)
    active_sticker_pack = Column(Integer, ForeignKey('sticker_packs.id'), nullable=True)
    settings = Column(JSON)

    # Отношения
    calendar_connections = relationship("CalendarConnection", back_populates="user_profile")
    owned_sticker_packs = relationship("UserStickerPack", back_populates="user_profile")
    transactions = relationship("CoinTransaction", back_populates="user_profile")
    gifts = relationship("Gift", back_populates="user_profile")

class CalendarConnection(Base):
    """Подключение к календарю"""
    __tablename__ = 'calendar_connections'

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(Integer, ForeignKey('user_profiles.id'))
    calendar_type = Column(SQLAlchemyEnum(CalendarType))
    calendar_id = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    token_expires = Column(DateTime)
    is_primary = Column(Boolean, default=False)
    sync_enabled = Column(Boolean, default=True)

    # Отношения
    user_profile = relationship("UserProfile", back_populates="calendar_connections")
    events = relationship("CalendarEvent", back_populates="calendar")

class CalendarEvent(Base):
    """События календаря"""
    __tablename__ = 'calendar_events'

    id = Column(Integer, primary_key=True)
    calendar_id = Column(Integer, ForeignKey('calendar_connections.id'))
    external_id = Column(String)
    title = Column(String)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_all_day = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)
    importance = Column(Integer, default=1)

    # Отношения
    calendar = relationship("CalendarConnection", back_populates="events")
    plan = relationship("Plan")

class StickerPack(Base):
    """Пак стикеров"""
    __tablename__ = 'sticker_packs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    is_premium = Column(Boolean, default=False)
    stickers = Column(JSON)

class UserStickerPack(Base):
    """Связь пользователя и пака стикеров"""
    __tablename__ = 'user_sticker_packs'

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(Integer, ForeignKey('user_profiles.id'))
    sticker_pack_id = Column(Integer, ForeignKey('sticker_packs.id'))
    purchased_at = Column(DateTime, default=datetime.utcnow)

    # Отношения
    user_profile = relationship("UserProfile", back_populates="owned_sticker_packs")
    sticker_pack = relationship("StickerPack")

class CoinTransaction(Base):
    """Транзакции с коинами"""
    __tablename__ = 'coin_transactions'

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(Integer, ForeignKey('user_profiles.id'))
    amount = Column(Integer)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Отношения
    user_profile = relationship("UserProfile", back_populates="transactions")

class Gift(Base):
    """Подарки между пользователями"""
    __tablename__ = 'gifts'

    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('user_profiles.id'))
    to_user_id = Column(Integer, ForeignKey('user_profiles.id'))
    item_type = Column(String)
    item_id = Column(Integer, nullable=True)
    amount = Column(Integer, nullable=True)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_anonymous = Column(Boolean, default=False)

    # Отношения
    user_profile = relationship("UserProfile", back_populates="gifts")