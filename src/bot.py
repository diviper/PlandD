import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.types.callback_query import CallbackQuery

from pland.config import Config
from pland.services import TaskService
from pland.db import Database, Task

async def list_tasks_handler(message: Message):
    """
    Обработчик команды /list с инлайн-кнопками
    """
    db = Database()
    try:
        tasks = db.get_tasks(message.from_user.id)
        if not tasks:
            await message.answer("У вас пока нет задач.")
            return

        # Создаем инлайн-клавиатуру со списком задач
        keyboard_markup = InlineKeyboardMarkup(row_width=1)
        keyboard_buttons = []

        for task in tasks:
            status = "✅" if task.completed else "⏳"
            button_text = f"{status} ID:{task.id} - {task.description[:20]}..."
            keyboard_buttons.append(
                InlineKeyboardButton(
                    text=button_text, 
                    callback_data=f"task_details:{task.id}"
                )
            )

        keyboard_markup.add(*keyboard_buttons)
        keyboard_markup.add(
            InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")
        )

        await message.answer("Ваши задачи:", reply_markup=keyboard_markup)
    except Exception as e:
        await message.answer(f"Ошибка при получении списка задач: {e}")
    finally:
        db.close()

async def task_details_handler(callback: CallbackQuery):
    """
    Обработчик нажатия на задачу для просмотра деталей
    """
    task_id = int(callback.data.split(':')[1])
    db = Database()
    
    try:
        # Получаем детали задачи (здесь нужно добавить метод в базу данных)
        task = db.get_task_by_id(task_id)
        
        # Создаем инлайн-клавиатуру с действиями
        keyboard_markup = InlineKeyboardMarkup(row_width=2)
        keyboard_markup.add(
            InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_task:{task_id}"),
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_task:{task_id}"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_list")
        )

        # Форматируем информацию о задаче
        task_info = (
            f"📋 Задача ID: {task.id}\n"
            f"📝 Описание: {task.description}\n"
            f"🏷️ Приоритет: {task.priority}\n"
            f"📅 Создана: {task.created_at}\n"
            f"🕒 Напоминание: {task.reminder_time or 'Не установлено'}\n"
            f"✅ Статус: {'Выполнена' if task.completed else 'В процессе'}"
        )

        await callback.message.edit_text(
            task_info, 
            reply_markup=keyboard_markup
        )
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")
    finally:
        db.close()

async def delete_task_handler(callback: CallbackQuery):
    """
    Обработчик удаления задачи
    """
    task_id = int(callback.data.split(':')[1])
    db = Database()
    
    try:
        db.delete_task(task_id)
        await callback.answer("Задача удалена")
        
        # Возвращаемся к списку задач
        await list_tasks_handler(callback.message)
    except Exception as e:
        await callback.answer(f"Ошибка при удалении: {e}")
    finally:
        db.close()

async def start_bot():
    """
    Запуск бота с поддержкой инлайн-кнопок
    """
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация обработчиков команд и колбэков
    dp.message.register(list_tasks_handler, Command("list"))
    dp.callback_query.register(task_details_handler, lambda c: c.data.startswith("task_details:"))
    dp.callback_query.register(delete_task_handler, lambda c: c.data.startswith("delete_task:"))

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.close()