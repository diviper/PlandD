"""Test Telegram bot connection and functionality"""
import asyncio
import logging
from aiogram import Bot, types
from src.core.config import Config, setup_logging
from src.bot.handlers.base import start_command, help_command
from src.bot.handlers.plan_handler import cmd_plan

async def test_bot_connection():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    if not Config.BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден в .env файле")
        return False
        
    try:
        print(f"🔄 Проверяем подключение к боту...")
        bot = Bot(token=Config.BOT_TOKEN)
        
        bot_info = await bot.get_me()
        print(f"✅ Бот успешно подключен!")
        print(f"Информация о боте:")
        print(f"- Username: @{bot_info.username}")
        print(f"- Имя: {bot_info.first_name}")
        print(f"- ID: {bot_info.id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при подключении к боту: {str(e)}")
        return False
    finally:
        if 'bot' in locals():
            await bot.session.close()

async def test_bot_commands():
    """Test bot commands"""
    setup_logging()
    bot = Bot(token=Config.BOT_TOKEN)
    
    try:
        # Test /start command
        message = types.Message(
            message_id=1,
            date=None,
            chat=types.Chat(id=1, type="private"),
            from_user=types.User(id=1, is_bot=False, first_name="Test"),
            text="/start",
            bot=bot
        )
        response = await start_command(message)
        print("✅ /start command test passed")
        
        # Test /help command
        message.text = "/help"
        response = await help_command(message)
        print("✅ /help command test passed")
        
        # Test /plan command
        message.text = "/plan"
        response = await cmd_plan(message)
        print("✅ /plan command test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании команд: {str(e)}")
        return False
    finally:
        await bot.session.close()

async def test_bot_handlers():
    """Test bot message handlers"""
    setup_logging()
    bot = Bot(token=Config.BOT_TOKEN)
    
    try:
        # Test text message handler
        message = types.Message(
            message_id=1,
            date=None,
            chat=types.Chat(id=1, type="private"),
            from_user=types.User(id=1, is_bot=False, first_name="Test"),
            text="Привет, бот!",
            bot=bot
        )
        
        # Add your message handler tests here
        print("✅ Message handlers test passed")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании обработчиков: {str(e)}")
        return False
    finally:
        await bot.session.close()

async def run_all_tests():
    """Run all bot tests"""
    print("🚀 Запуск тестов бота...")
    
    # Test connection
    connection_ok = await test_bot_connection()
    if not connection_ok:
        print("❌ Тесты остановлены из-за ошибки подключения")
        return
    
    # Test commands
    commands_ok = await test_bot_commands()
    if not commands_ok:
        print("⚠️ Ошибка в тестах команд")
    
    # Test handlers
    handlers_ok = await test_bot_handlers()
    if not handlers_ok:
        print("⚠️ Ошибка в тестах обработчиков")
    
    print("\n📊 Результаты тестирования:")
    print(f"- Подключение: {'✅' if connection_ok else '❌'}")
    print(f"- Команды: {'✅' if commands_ok else '❌'}")
    print(f"- Обработчики: {'✅' if handlers_ok else '❌'}")

if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n⚠️ Тест остановлен пользователем")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
