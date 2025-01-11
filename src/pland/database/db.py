"""Database configuration module"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pland.core.config import Config

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(f'sqlite:///{Config.DATABASE_PATH}')

# Create session factory
Session = sessionmaker(bind=engine)

# Create base class for declarative models
Base = declarative_base()

def init_db():
    """Initialize database"""
    try:
        # Import models to ensure they are registered with Base
        from . import models
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise
