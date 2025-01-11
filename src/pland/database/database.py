"""Database module for PlanD"""
import logging
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict

from pland.core.config import Config
from pland.database.models import Task, Schedule, Meal, ReminderSettings

logger = logging.getLogger(__name__)

class Database:
    """Database handler class"""
    def __init__(self, db_path: Optional[str] = None, test_conn: Optional[sqlite3.Connection] = None):
        """Initialize database"""
        self.db_path = db_path or Config.DATABASE_PATH
        self._test_conn = test_conn
        self._create_tables()
        logger.info(f"Database initialized: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection - either test or new one"""
        if self._test_conn is not None:
            return self._test_conn
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        logger.debug(f"Creating tables in database: {self.db_path}")

        # SQL statements for creating tables
        CREATE_TASKS_TABLE = """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                due_date TIMESTAMP NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                parent_task_id INTEGER,
                estimated_duration INTEGER,
                energy_level INTEGER,
                energy_type TEXT,
                optimal_time TEXT,
                category TEXT,
                focus_required TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """

        CREATE_SCHEDULES_TABLE = """
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                sleep_time TEXT,
                wake_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        CREATE_MEALS_TABLE = """
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_time TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        CREATE_REMINDER_SETTINGS_TABLE = """
            CREATE TABLE IF NOT EXISTS reminder_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                default_reminder_time INTEGER DEFAULT 30,
                morning_reminder_time TEXT DEFAULT '09:00',
                evening_reminder_time TEXT DEFAULT '20:00',
                priority_high_interval INTEGER DEFAULT 30,
                priority_medium_interval INTEGER DEFAULT 60,
                priority_low_interval INTEGER DEFAULT 120,
                quiet_hours_start TEXT DEFAULT '23:00',
                quiet_hours_end TEXT DEFAULT '07:00',
                reminder_types TEXT DEFAULT 'all',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")

            # Create tables
            cursor.execute(CREATE_TASKS_TABLE)
            cursor.execute(CREATE_SCHEDULES_TABLE)
            cursor.execute(CREATE_MEALS_TABLE)
            cursor.execute(CREATE_REMINDER_SETTINGS_TABLE)

            # Verify tables were created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            logger.info(f"Created tables: {[table[0] for table in tables]}")

            if self._test_conn is None:
                conn.commit()
                conn.close()
            else:
                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise

    def add_task(self, task: Task) -> int:
        """Add a new task to the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO tasks (
                    user_id, title, description, priority, due_date, completed,
                    parent_task_id, estimated_duration, energy_level, energy_type,
                    optimal_time, category, focus_required
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.user_id, task.title, task.description, task.priority,
                    task.due_date.strftime(Config.DATETIME_FORMAT), task.completed,
                    task.parent_task_id, task.estimated_duration, task.energy_level,
                    task.energy_type, task.optimal_time, task.category, task.focus_required
                )
            )
            task_id = cursor.lastrowid
            if task_id is None:
                raise sqlite3.Error("Failed to get lastrowid after insert")
            conn.commit()
            if self._test_conn is None:
                conn.close()
            logger.debug(f"Added task with ID: {task_id}")
            return task_id
        except sqlite3.Error as e:
            logger.error(f"Error adding task: {str(e)}")
            raise

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a specific task by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, title, description, priority, due_date, completed,
                   parent_task_id, estimated_duration, energy_level, energy_type,
                   optimal_time, category, focus_required
            FROM tasks WHERE id = ?
            """, 
            (task_id,)
        )
        row = cursor.fetchone()
        if self._test_conn is None:
            conn.close()
        if row:
            return Task(
                id=row[0],
                user_id=row[1],
                title=row[2],
                description=row[3],
                priority=row[4],
                due_date=datetime.strptime(row[5], Config.DATETIME_FORMAT),
                completed=bool(row[6]),
                parent_task_id=row[7],
                estimated_duration=row[8],
                energy_level=row[9],
                energy_type=row[10],
                optimal_time=row[11],
                category=row[12],
                focus_required=row[13]
            )
        return None

    def get_tasks(self, user_id: int) -> List[Task]:
        """Get all tasks for a specific user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, title, description, priority, due_date, completed,
                   parent_task_id, estimated_duration, energy_level, energy_type,
                   optimal_time, category, focus_required
            FROM tasks WHERE user_id = ?
            """, 
            (user_id,)
        )
        tasks = [Task(
            id=row[0],
            user_id=row[1],
            title=row[2],
            description=row[3],
            priority=row[4],
            due_date=datetime.strptime(row[5], Config.DATETIME_FORMAT),
            completed=bool(row[6]),
            parent_task_id=row[7],
            estimated_duration=row[8],
            energy_level=row[9],
            energy_type=row[10],
            optimal_time=row[11],
            category=row[12],
            focus_required=row[13]
        ) for row in cursor.fetchall()]
        if self._test_conn is None:
            conn.close()
        return tasks

    def update_reminder_settings(self, settings: ReminderSettings) -> bool:
        """Update or create reminder settings for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO reminder_settings (
                    user_id, default_reminder_time, morning_reminder_time,
                    evening_reminder_time, priority_high_interval,
                    priority_medium_interval, priority_low_interval,
                    quiet_hours_start, quiet_hours_end, reminder_types,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    settings.user_id, settings.default_reminder_time,
                    settings.morning_reminder_time, settings.evening_reminder_time,
                    settings.priority_high_interval, settings.priority_medium_interval,
                    settings.priority_low_interval, settings.quiet_hours_start,
                    settings.quiet_hours_end, ','.join(settings.reminder_types)
                )
            )
            conn.commit()
            if self._test_conn is None:
                conn.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating reminder settings: {str(e)}")
            return False

    def get_reminder_settings(self, user_id: int) -> Optional[ReminderSettings]:
        """Get reminder settings for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reminder_settings WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if self._test_conn is None:
            conn.close()

        if row:
            return ReminderSettings(
                id=row[0],
                user_id=row[1],
                default_reminder_time=row[2],
                morning_reminder_time=row[3],
                evening_reminder_time=row[4],
                priority_high_interval=row[5],
                priority_medium_interval=row[6],
                priority_low_interval=row[7],
                quiet_hours_start=row[8],
                quiet_hours_end=row[9],
                reminder_types=row[10].split(',') if row[10] else ['all']
            )
        return None

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from the database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, title, description, priority, due_date, completed,
                   parent_task_id, estimated_duration, energy_level, energy_type,
                   optimal_time, category, focus_required
            FROM tasks
            """
        )
        tasks = [Task(
            id=row[0],
            user_id=row[1],
            title=row[2],
            description=row[3],
            priority=row[4],
            due_date=datetime.strptime(row[5], Config.DATETIME_FORMAT),
            completed=bool(row[6]),
            parent_task_id=row[7],
            estimated_duration=row[8],
            energy_level=row[9],
            energy_type=row[10],
            optimal_time=row[11],
            category=row[12],
            focus_required=row[13]
        ) for row in cursor.fetchall()]
        if self._test_conn is None:
            conn.close()
        return tasks

    def get_upcoming_tasks(self, user_id: int) -> List[Task]:
        """Get upcoming tasks for a specific user"""
        current_time = datetime.now().strftime(Config.DATETIME_FORMAT)
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, title, description, priority, due_date, completed,
                   parent_task_id, estimated_duration, energy_level, energy_type,
                   optimal_time, category, focus_required
            FROM tasks 
            WHERE user_id = ? AND due_date > ? AND completed = FALSE
            ORDER BY due_date ASC
        """, (user_id, current_time))
        tasks = [Task(
            id=row[0],
            user_id=row[1],
            title=row[2],
            description=row[3],
            priority=row[4],
            due_date=datetime.strptime(row[5], Config.DATETIME_FORMAT),
            completed=bool(row[6]),
            parent_task_id=row[7],
            estimated_duration=row[8],
            energy_level=row[9],
            energy_type=row[10],
            optimal_time=row[11],
            category=row[12],
            focus_required=row[13]
        ) for row in cursor.fetchall()]
        if self._test_conn is None:
            conn.close()
        return tasks

    def update_task_status(self, task_id: int, completed: bool):
        """Update task completion status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (completed, task_id)
        )
        conn.commit()
        if self._test_conn is None:
            conn.close()

    def delete_task(self, task_id: int):
        """Delete a task by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        if self._test_conn is None:
            conn.close()

    def update_schedule(self, schedule: Schedule):
        """Update or create a user's schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO schedules (user_id, sleep_time, wake_time)
            VALUES (?, ?, ?)
            """,
            (schedule.user_id, schedule.sleep_time, schedule.wake_time)
        )
        conn.commit()
        if self._test_conn is None:
            conn.close()

    def add_meal(self, meal: Meal):
        """Add a new meal schedule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO meals (user_id, meal_time, meal_type)
            VALUES (?, ?, ?)
            """,
            (meal.user_id, meal.meal_time, meal.meal_type)
        )
        conn.commit()
        if self._test_conn is None:
            conn.close()