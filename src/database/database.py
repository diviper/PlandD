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
        
        database_dir = os.path.dirname(Config.DATABASE_PATH)
        logger.info(f"Database directory: {database_dir}")
        
        # Create database directory if it doesn't exist
        if database_dir:  # Проверяем, что путь не пустой
            os.makedirs(database_dir, exist_ok=True)
        
        # Create engine and session factory
        database_url = f'sqlite:///{Config.DATABASE_PATH}'
        logger.info(f"Database URL: {database_url}")
        
        self.engine = create_engine(database_url)
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

    async def get_all_plans(self) -> List[Plan]:
        """Get all plans from the database"""
        async with self._lock:
            session = self.get_session()
            try:
                plans = session.execute(select(Plan)).scalars().all()
                logger.debug(f"Retrieved {len(plans)} plans")
                return plans
            finally:
                session.close()

    @staticmethod
    def init_db():
        """Initialize database and create all tables"""
        logger.info("Initializing database...")
        
        # Создаем URL для SQLite
        database_url = f"sqlite:///{Config.DATABASE_PATH}"
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        logger.info("Database initialized successfully")
        return Session()

    async def get_plan(self, plan_id: int) -> Optional[Plan]:
        """Get plan by ID"""
        try:
            stmt = select(Plan).where(Plan.id == plan_id)
            result = self.get_session().execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting plan {plan_id}: {str(e)}")
            return None

    async def get_user_plans(self, user_id: int) -> List[Plan]:
        """Get all plans for user"""
        try:
            stmt = select(Plan).where(Plan.user_id == user_id)
            result = self.get_session().execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting plans for user {user_id}: {str(e)}")
            return []

    async def create_plan(self, user_id: int, plan_data: Dict) -> Optional[Plan]:
        """Create new plan"""
        try:
            plan = Plan(
                user_id=user_id,
                type=plan_data.get('type', 'personal'),
                title=plan_data['title'],
                description=plan_data.get('description', ''),
                estimated_duration=plan_data.get('estimated_duration'),
                priority=plan_data.get('priority', 'medium'),
                created_at=datetime.utcnow()
            )
            self.get_session().add(plan)
            self.get_session().commit()
            return plan
        except Exception as e:
            logger.error(f"Error creating plan for user {user_id}: {str(e)}")
            self.get_session().rollback()
            return None

    async def update_plan(self, plan_id: int, plan_data: Dict) -> bool:
        """Update existing plan"""
        try:
            plan = await self.get_plan(plan_id)
            if not plan:
                return False
            
            for key, value in plan_data.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)
            
            self.get_session().commit()
            return True
        except Exception as e:
            logger.error(f"Error updating plan {plan_id}: {str(e)}")
            self.get_session().rollback()
            return False

    async def delete_plan(self, plan_id: int) -> bool:
        """Delete plan"""
        try:
            plan = await self.get_plan(plan_id)
            if not plan:
                return False
            
            self.get_session().delete(plan)
            self.get_session().commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting plan {plan_id}: {str(e)}")
            self.get_session().rollback()
            return False

    async def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        try:
            stmt = select(UserPreferences).where(UserPreferences.user_id == user_id)
            result = self.get_session().execute(stmt)
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {str(e)}")
            return None

    async def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update user preferences"""
        try:
            prefs = await self.get_user_preferences(user_id)
            if not prefs:
                prefs = UserPreferences(user_id=user_id)
                self.get_session().add(prefs)
            
            for key, value in preferences.items():
                if hasattr(prefs, key):
                    setattr(prefs, key, value)
            
            self.get_session().commit()
            return True
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {str(e)}")
            self.get_session().rollback()
            return False