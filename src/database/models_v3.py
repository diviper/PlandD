"""Models for PlanD Bot v0.7.0 - Premium Features"""

from datetime import datetime, time
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

class PremiumFeature(Enum):
    """Премиум функции"""
    CALENDAR_SYNC = "calendar_sync"
    CUSTOM_STYLE = "custom_style"
    STICKER_PACKS = "sticker_packs"
    GIFTS = "gifts"
    AI_CREATIVITY = "ai_creativity"

class UserProfile(Base):
    """Расширенный профиль пользователя"""
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    coins = Column(Integer, default=0)
    interaction_style = Column(SQLEnum(InteractionStyle), default=InteractionStyle.RICK)
    premium_until = Column(DateTime, nullable=True)
    active_sticker_pack = Column(Integer, ForeignKey('sticker_packs.id'), nullable=True)
    settings = Column(JSON)  # Пользовательские настройки в JSON

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
    calendar_type = Column(SQLEnum(CalendarType))
    calendar_id = Column(String)  # ID календаря в соответствующем сервисе
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
    external_id = Column(String)  # ID события в календаре
    title = Column(String)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_all_day = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String, nullable=True)
    importance = Column(Integer, default=1)  # 1-5, где 5 - самое важное

    # Отношения
    calendar = relationship("CalendarConnection", back_populates="events")

class StickerPack(Base):
    """Пак стикеров"""
    __tablename__ = 'sticker_packs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)  # Цена в коинах
    is_premium = Column(Boolean, default=False)
    stickers = Column(JSON)  # Список стикеров в JSON

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
    amount = Column(Integer)  # Положительное или отрицательное число
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
    item_type = Column(String)  # sticker_pack, coins, premium_days
    item_id = Column(Integer, nullable=True)
    amount = Column(Integer, nullable=True)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_anonymous = Column(Boolean, default=False)

    # Отношения
    user_profile = relationship("UserProfile", back_populates="gifts")

# Обновляем существующие модели для поддержки премиум функций

class Plan(Base):
    """План с поддержкой календаря"""
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    calendar_event_id = Column(Integer, ForeignKey('calendar_events.id'), nullable=True)
    title = Column(String)
    description = Column(String)
    time_block = Column(SQLEnum(TimeBlock))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    priority = Column(SQLEnum(Priority))
    is_flexible = Column(Boolean, default=True)  # Можно ли перемещать план
    reminder_times = Column(JSON)  # Список времен для напоминаний в JSON
    completion_reward = Column(Integer, default=10)  # Награда в коинах

    # Отношения
    calendar_event = relationship("CalendarEvent")
    steps = relationship("PlanStep", back_populates="plan")

class PlanStep(Base):
    """Шаг плана с наградой"""
    __tablename__ = 'plan_steps'

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('plans.id'))
    title = Column(String)
    duration_minutes = Column(Integer)
    priority = Column(SQLEnum(Priority))
    order = Column(Integer)
    completion_reward = Column(Integer, default=5)  # Награда в коинах

    # Отношения
    plan = relationship("Plan", back_populates="steps")
