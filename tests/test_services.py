"""Test services functionality"""
import pytest
from src.services.ai.ai_service import AIService
from src.services.reminder.scheduler import ReminderScheduler

def test_ai_service(config):
    """Test AI service initialization"""
    service = AIService(config)
    assert service is not None
    assert hasattr(service, 'client')  # Проверяем наличие клиента OpenAI

@pytest.mark.asyncio
async def test_reminder_scheduler(bot, db):
    """Test reminder scheduler initialization"""
    scheduler = ReminderScheduler(bot, db)
    assert scheduler is not None
    assert scheduler.scheduler is not None
    assert scheduler.bot == bot
    assert scheduler.db == db
