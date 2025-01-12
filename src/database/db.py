"""Database initialization module"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import Config
from src.database.base import Base
from src.database.models import Plan, PlanStep, PlanProgress, UserPreferences

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database and create all tables"""
    logger.info("Initializing database...")
    
    # Создаем URL для SQLite
    database_url = f"sqlite:///{Config.DATABASE_PATH}"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    logger.info("Database initialized successfully")
