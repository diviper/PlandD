import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

@dataclass
class Task:
    description: str
    priority: str = 'medium'
    created_at: datetime = datetime.now()
    reminder_time: datetime = None
    completed: bool = False
    id: int = None
    user_id: int = None

class Database:
    def __init__(self, db_path='tasks.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                description TEXT,
                priority TEXT,
                created_at DATETIME,
                reminder_time DATETIME,
                completed BOOLEAN
            )
        ''')
        self.conn.commit()

    def add_task(self, task: Task) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO tasks (user_id, description, priority, created_at, reminder_time, completed) VALUES (?, ?, ?, ?, ?, ?)',
            (task.user_id, task.description, task.priority, task.created_at, task.reminder_time, task.completed)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_tasks(self, user_id: int, completed: Optional[bool] = None) -> List[Task]:
        cursor = self.conn.cursor()
        if completed is None:
            cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
        else:
            cursor.execute('SELECT * FROM tasks WHERE user_id = ? AND completed = ?', (user_id, completed))
        
        tasks = []
        for row in cursor.fetchall():
            task = Task(
                id=row[0],
                user_id=row[1],
                description=row[2],
                priority=row[3],
                created_at=datetime.fromisoformat(row[4]),
                reminder_time=datetime.fromisoformat(row[5]) if row[5] else None,
                completed=bool(row[6])
            )
            tasks.append(task)
        return tasks

    def get_task_by_id(self, task_id: int) -> Task:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Задача с ID {task_id} не найдена")
        
        return Task(
            id=row[0],
            user_id=row[1],
            description=row[2],
            priority=row[3],
            created_at=datetime.fromisoformat(row[4]),
            reminder_time=datetime.fromisoformat(row[5]) if row[5] else None,
            completed=bool(row[6])
        )

    def update_task(self, task_id: int, description: str = None, 
                    priority: str = None, reminder_time: datetime = None):
        cursor = self.conn.cursor()
        updates = []
        params = []

        if description:
            updates.append('description = ?')
            params.append(description)
        if priority:
            updates.append('priority = ?')
            params.append(priority)
        if reminder_time:
            updates.append('reminder_time = ?')
            params.append(reminder_time)

        if updates:
            query = f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?'
            params.append(task_id)
            cursor.execute(query, tuple(params))
            self.conn.commit()

    def delete_task(self, task_id: int):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()

    def get_tasks_with_reminders(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE user_id = ? AND reminder_time IS NOT NULL AND completed = 0', (user_id,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()