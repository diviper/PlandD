"""Database module for PlanD"""
import logging
import os
from datetime import datetime
from typing import List, Optional, Dict
import asyncio

from sqlalchemy import create_engine, select, or_, and_
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import Config
from src.database.models import Plan, PlanStep, PlanProgress, UserPreferences
from src.database.base import Base

logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
# Base = declarative_base()

class Database:
    """Database handler class"""
    def __init__(self):
        """Initialize database"""
        logger.info(f"Initializing database: {Config.DATABASE_PATH}")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
        
        # Create engine and session factory
        self.engine = create_engine(f'sqlite:///{Config.DATABASE_PATH}')
        self.session_factory = sessionmaker(bind=self.engine)
        self._lock = asyncio.Lock()
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")

    def get_session(self) -> Session:
        """Get database session"""
        return self.session_factory()

    async def add_plan(self, plan: Plan) -> int:
        """Add a new plan to the database"""
        async with self._lock:
            session = self.get_session()
            try:
                session.add(plan)
                session.commit()
                plan_id = plan.id
                logger.debug(f"Added plan with ID: {plan_id}")
                return plan_id
            except Exception as e:
                logger.error(f"Error adding plan: {str(e)}")
                session.rollback()
                raise
            finally:
                session.close()

    async def get_plan(self, plan_id: int) -> Optional[Dict]:
        """Get plan by ID with all related data"""
        async with self._lock:
            session = self.get_session()
            try:
                plan = session.query(Plan).filter_by(id=plan_id).first()
                if not plan:
                    return None

                # Get steps and progress
                steps = session.query(PlanStep).filter_by(plan_id=plan_id).all()
                progress = session.query(PlanProgress).filter_by(plan_id=plan_id).all()

                # Convert to dict
                return {
                    'id': plan.id,
                    'user_id': plan.user_id,
                    'type': plan.type,
                    'title': plan.title,
                    'description': plan.description,
                    'estimated_duration': plan.estimated_duration,
                    'priority': plan.priority,
                    'created_at': plan.created_at.isoformat(),
                    'steps': [
                        {
                            'id': step.id,
                            'title': step.title,
                            'description': step.description,
                            'duration': step.duration,
                            'prerequisites': step.prerequisites,
                            'metrics': step.metrics
                        } for step in steps
                    ],
                    'progress': [
                        {
                            'step_id': prog.step_id,
                            'status': prog.status,
                            'completed_at': prog.completed_at.isoformat() if prog.completed_at else None,
                            'notes': prog.notes
                        } for prog in progress
                    ]
                }
            except Exception as e:
                logger.error(f"Error getting plan {plan_id}: {str(e)}")
                return None
            finally:
                session.close()

    async def update_plan_progress(self, progress: PlanProgress) -> bool:
        """Update progress for a plan step"""
        async with self._lock:
            session = self.get_session()
            try:
                session.add(progress)
                session.commit()
                logger.debug(f"Updated progress for step {progress.step_id}")
                return True
            except Exception as e:
                logger.error(f"Error updating progress: {str(e)}")
                session.rollback()
                return False
            finally:
                session.close()

    async def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        async with self._lock:
            session = self.get_session()
            try:
                return session.query(UserPreferences).filter_by(user_id=user_id).first()
            except Exception as e:
                logger.error(f"Error getting user preferences: {str(e)}")
                return None
            finally:
                session.close()

    async def update_user_preferences(self, prefs: UserPreferences) -> bool:
        """Update user preferences"""
        async with self._lock:
            session = self.get_session()
            try:
                session.merge(prefs)
                session.commit()
                logger.debug(f"Updated preferences for user {prefs.user_id}")
                return True
            except Exception as e:
                logger.error(f"Error updating preferences: {str(e)}")
                session.rollback()
                return False
            finally:
                session.close()