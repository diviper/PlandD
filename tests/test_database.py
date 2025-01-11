"""Database tests"""
import pytest
from datetime import datetime, timedelta

from pland.database.models import Task, Schedule, Meal
from pland.core.config import Config

def test_add_task(test_db):
    """Test adding a task to the database"""
    task = Task(
        id=None,
        user_id=1,
        title="Test Task",
        description="Test Description",
        priority=Config.PRIORITY_HIGH,  # Using constant from Config
        due_date=datetime.now(),
        completed=False
    )
    task_id = test_db.add_task(task)
    assert task_id is not None

    tasks = test_db.get_tasks(1)
    assert len(tasks) == 1
    assert tasks[0].title == "Test Task"
    assert tasks[0].priority == Config.PRIORITY_HIGH

def test_get_upcoming_tasks(test_db):
    """Test getting upcoming tasks"""
    # Add tasks with different dates
    future_date = datetime.now() + timedelta(days=1)
    past_date = datetime.now() - timedelta(days=1)

    future_task = Task(
        id=None,
        user_id=1,
        title="Future Task",
        description="Test Description",
        priority=Config.PRIORITY_HIGH,
        due_date=future_date,
        completed=False
    )
    past_task = Task(
        id=None,
        user_id=1,
        title="Past Task",
        description="Test Description",
        priority=Config.PRIORITY_LOW,
        due_date=past_date,
        completed=False
    )

    test_db.add_task(future_task)
    test_db.add_task(past_task)

    upcoming_tasks = test_db.get_upcoming_tasks(1)
    assert len(upcoming_tasks) == 1
    assert upcoming_tasks[0].title == "Future Task"

def test_update_task_status(test_db):
    """Test updating task status"""
    task = Task(
        id=None,
        user_id=1,
        title="Test Task",
        description="Test Description",
        priority=Config.PRIORITY_MEDIUM,
        due_date=datetime.now(),
        completed=False
    )
    task_id = test_db.add_task(task)

    test_db.update_task_status(task_id, completed=True)
    updated_task = test_db.get_task(task_id)
    assert updated_task.completed is True

def test_delete_task(test_db):
    """Test deleting a task"""
    task = Task(
        id=None,
        user_id=1,
        title="Test Task",
        description="Test Description",
        priority=Config.PRIORITY_LOW,
        due_date=datetime.now(),
        completed=False
    )
    task_id = test_db.add_task(task)

    test_db.delete_task(task_id)
    deleted_task = test_db.get_task(task_id)
    assert deleted_task is None

def test_update_schedule(test_db):
    """Test updating user schedule"""
    schedule = Schedule(
        id=None,
        user_id=1,
        sleep_time="23:00",
        wake_time="07:00"
    )
    test_db.update_schedule(schedule)

def test_add_meal(test_db):
    """Test adding meal schedule"""
    meal = Meal(
        id=None,
        user_id=1,
        meal_time="12:00",
        meal_type="lunch"
    )
    test_db.add_meal(meal)