"""Models module for PlanD database"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Task:
    """Task model representing a user's task"""
    id: Optional[int]
    user_id: int
    title: str
    description: Optional[str]
    priority: str
    due_date: datetime
    completed: bool = False
    # Расширенные параметры задачи
    parent_task_id: Optional[int] = None  # Для иерархии задач
    estimated_duration: Optional[int] = None  # В минутах
    energy_level: Optional[int] = None  # От 1 до 10
    energy_type: Optional[str] = None  # mental/physical/emotional
    optimal_time: Optional[str] = None  # morning/afternoon/evening
    category: Optional[str] = None  # Категория задачи
    focus_required: Optional[str] = None  # Уровень концентрации

@dataclass
class Schedule:
    """Schedule model representing a user's daily schedule"""
    id: Optional[int]
    user_id: int
    sleep_time: Optional[str]
    wake_time: Optional[str]

@dataclass
class Meal:
    """Meal model representing a user's meal schedule"""
    id: Optional[int]
    user_id: int
    meal_time: str
    meal_type: str

@dataclass
class ReminderSettings:
    """Model for user's reminder preferences"""
    id: Optional[int]
    user_id: int
    default_reminder_time: int = 30  # Minutes before task
    morning_reminder_time: str = "09:00"  # Daily morning summary time
    evening_reminder_time: str = "20:00"  # Daily evening summary time
    priority_high_interval: int = 30  # Minutes between high priority reminders
    priority_medium_interval: int = 60  # Minutes between medium priority reminders
    priority_low_interval: int = 120  # Minutes between low priority reminders
    quiet_hours_start: str = "23:00"  # Start of quiet hours
    quiet_hours_end: str = "07:00"  # End of quiet hours
    reminder_types: List[str] = None  # Types of reminders to receive ('all' or specific types)