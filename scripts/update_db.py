"""Script to update database schema"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Base
from sqlalchemy import create_engine
from src.core.config import Config

def update_database():
    """Update database schema"""
    print("Updating database schema...")
    
    # Create database directory if it doesn't exist
    database_dir = os.path.dirname(Config.DATABASE_PATH)
    if database_dir:
        os.makedirs(database_dir, exist_ok=True)
    
    # Create engine
    database_url = f'sqlite:///{Config.DATABASE_PATH}'
    engine = create_engine(database_url)
    
    # Drop all tables and recreate them
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    print("Database schema updated successfully!")

if __name__ == '__main__':
    update_database()
