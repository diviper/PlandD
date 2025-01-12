"""Test handlers functionality"""
import pytest
from datetime import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.methods import SendMessage
from src.bot.handlers.base import start_command, help_command, handle_text_message
from src.bot.handlers.plan_handler import cmd_plan

async def create_message(text: str, bot) -> types.Message:
    """Create a test message"""
    message = types.Message(
        message_id=1,
        date=datetime.now(),
        chat=types.Chat(id=1, type="private"),
        from_user=types.User(id=1, is_bot=False, first_name="Test", username="test"),
        text=text,
        bot=bot
    )
    return message

@pytest.mark.asyncio
async def test_start_command(bot):
    """Test /start command"""
    message = await create_message("/start", bot)
    result = await start_command(message)
    assert isinstance(result, SendMessage)

@pytest.mark.asyncio
async def test_help_command(bot):
    """Test /help command"""
    message = await create_message("/help", bot)
    result = await help_command(message)
    assert isinstance(result, SendMessage)

@pytest.mark.asyncio
async def test_handle_text_message(bot):
    """Test text message handling"""
    message = await create_message("📝 новый план", bot)
    result = await handle_text_message(message)
    assert isinstance(result, SendMessage)

@pytest.mark.asyncio
async def test_cmd_plan(bot, dp):
    """Test /plan command"""
    message = await create_message("/plan", bot)
    state = FSMContext(storage=dp.storage, key=StorageKey(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        bot_id=bot.id
    ))
    result = await cmd_plan(message, state)
    assert isinstance(result, SendMessage)
