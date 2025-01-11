"""Test configuration and fixtures"""
import logging
import sqlite3
import pytest
from pland.core.config import Config, setup_logging

# Setup logging for tests with DEBUG level
setup_logging(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def test_conn():
    """Create and maintain a single database connection for all tests"""
    logger.info("Creating test database connection")
    conn = sqlite3.connect(":memory:")
    yield conn
    logger.info("Closing test database connection")
    conn.close()

@pytest.fixture(scope="session")
def test_db(test_conn):
    """Create test database"""
    logger.info("Initializing test database")
    db = Database(db_path=":memory:", test_conn=test_conn)
    return db

@pytest.fixture
def test_config():
    """Get test configuration"""
    return Config