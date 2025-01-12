"""Initialize database script"""
from src.database.database import Database

if __name__ == "__main__":
    print("Initializing database...")
    db = Database()  # Это создаст базу данных и все таблицы
    print("Database initialized successfully!")
