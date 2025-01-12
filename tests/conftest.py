"""Pytest configuration file"""
import pytest
import pytest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.database.database import Database
from src.services.ai.ai_service import AIService
from src.core.config import Config

@pytest_asyncio.fixture(scope="session")
def config():
    """Return test configuration"""
    return Config()

@pytest_asyncio.fixture(scope="session")
async def bot(config):
    """Return test bot instance"""
    bot = Bot(token=config.BOT_TOKEN)
    yield bot
    await bot.session.close()

@pytest_asyncio.fixture(scope="session")
async def dp():
    """Return test dispatcher instance"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    yield dp
    await dp.storage.close()

@pytest_asyncio.fixture(scope="session")
def db():
    """Return test database instance"""
    database = Database()
    yield database

@pytest_asyncio.fixture(scope="session")
def ai_service(config):
    """Return test AI service instance"""
    return AIService(config)
