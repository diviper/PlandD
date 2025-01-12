"""Database connection module"""
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.core.config import Config

logger = logging.getLogger(__name__)

def ensure_db_directory():
    """Ensure database directory exists"""
    db_dir = os.path.dirname(Config.DATABASE_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created database directory: {db_dir}")

# Create database engine
engine = create_engine(f"sqlite:///{Config.DATABASE_PATH}")

# Create session factory
Session = sessionmaker(bind=engine)

# Create base class for declarative models
Base = declarative_base()

def init_db():
    """Initialize database"""
    try:
        # Ensure database directory exists
        ensure_db_directory()
        
        # Import models to ensure they are registered with Base
        from . import models
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise
