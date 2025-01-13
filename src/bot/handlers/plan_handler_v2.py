"""План-хендлер v2 с временной структурой"""
import logging
import traceback
from datetime import datetime, time
from typing import Dict, Any, Optional

from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage

from src.database.database import Database
from src.database.models_v2 import Plan, TimeBlock, Priority
from src.services.plan_service_v2 import PlanServiceV2
from src.services.ai.ai_service import AIService

# Настройка логирования
logger = logging.getLogger(__name__)

# Состояния для создания плана
class PlanStatesV2(StatesGroup):
    """Состояния для работы с планами v2"""
    WAITING_FOR_PLAN = State()    # Ожидание ввода плана
    WAITING_FOR_TIME = State()    # Ожидание времени
    CONFIRMING_PLAN = State()     # Подтверждение плана
    EDITING_PLAN = State()        # Редактирование плана

async def cmd_plan_v2(message: types.Message, state: FSMContext, db: Database) -> None:
    """Обработчик команды /plan"""
    try:
        # Очищаем предыдущее состояние
        await state.clear()
        
        # Создаем сервис
        plan_service = PlanServiceV2(db)
        
        # Получаем предпочтения пользователя
        prefs = plan_service.get_user_preferences(message.from_user.id)
        
        # Сохраняем данные в состоянии
        await state.update_data(
            user_id=message.from_user.id,
            preferences=prefs.to_dict() if prefs else None
        )
        
        # Устанавливаем состояние ожидания плана
        await state.set_state(PlanStatesV2.WAITING_FOR_PLAN)
        
        # Отправляем приветственное сообщение
        await message.answer(
            "🌀 *План 2.0, Морти!*\n\n"
            "Расскажи, что нужно сделать, а я помогу разбить это на конкретные временные блоки!\n\n"
            "Пример:\n"
            "```\n"
            "Нужно подготовить презентацию для встречи\n"
            "- Собрать данные\n"
            "- Сделать слайды\n"
            "- Отрепетировать\n"
            "```",
            parse_mode="Markdown"
        )
        logger.info(f"Пользователь {message.from_user.id} начал создание плана v2")
        
    except Exception as e:
        error_msg = f"Ошибка при запуске планирования v2: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "Упс, Морти! Что-то пошло не так при запуске.\n"
            "Попробуй еще раз или обратись к разработчикам."
        )

async def process_plan_input(message: types.Message, state: FSMContext, db: Database) -> None:
    """Обработка введенного плана"""
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        user_id = data['user_id']
        prefs = data.get('preferences', {})
        
        # Создаем сервис AI для анализа плана
        ai_service = AIService()
        
        # Анализируем план через AI
        ai_response = await ai_service.analyze_plan_v2(
            plan_text=message.text,
            user_preferences=prefs
        )
        
        # Сохраняем результат анализа
        await state.update_data(ai_plan=ai_response)
        
        # Запрашиваем время для плана
        time_blocks = "\n".join([
            "🌅 Утро (06:00-12:00)",
            "☀️ День (12:00-18:00)",
            "🌙 Вечер (18:00-23:00)"
        ])
        
        await state.set_state(PlanStatesV2.WAITING_FOR_TIME)
        await message.answer(
            "Отлично, Морти! Теперь выбери удобное время:\n\n"
            f"{time_blocks}\n\n"
            "Напиши время начала в формате ЧЧ:ММ",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [
                        types.KeyboardButton(text="09:00"),
                        types.KeyboardButton(text="14:00"),
                        types.KeyboardButton(text="19:00")
                    ]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        
    except Exception as e:
        error_msg = f"Ошибка при обработке плана v2: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "Упс, что-то пошло не так при анализе плана.\n"
            "Попробуй еще раз или опиши план подробнее."
        )

async def process_time_input(message: types.Message, state: FSMContext, db: Database) -> None:
    """Обработка введенного времени"""
    try:
        # Проверяем формат времени
        try:
            start_time = datetime.strptime(message.text, '%H:%M').time()
        except ValueError:
            await message.answer(
                "Некорректный формат времени! Используй формат ЧЧ:ММ, например: 09:30"
            )
            return
        
        # Получаем данные из состояния
        data = await state.get_data()
        ai_plan = data['ai_plan']
        
        # Определяем временной блок
        time_block = get_time_block(start_time)
        
        # Создаем план
        plan_service = PlanServiceV2(db)
        plan_data = {
            'title': ai_plan['title'],
            'description': ai_plan['description'],
            'time_block': time_block.value,
            'start_time': start_time.strftime('%H:%M'),
            'end_time': calculate_end_time(start_time, ai_plan['duration_minutes']).strftime('%H:%M'),
            'duration_minutes': ai_plan['duration_minutes'],
            'priority': ai_plan['priority'],
            'steps': ai_plan['steps']
        }
        
        # Сохраняем план для подтверждения
        await state.update_data(plan_data=plan_data)
        
        # Форматируем план для отображения
        plan_text = format_plan_preview(plan_data)
        
        # Отправляем на подтверждение
        await state.set_state(PlanStatesV2.CONFIRMING_PLAN)
        await message.answer(
            f"Вот твой план, Морти!\n\n{plan_text}\n\nВсё верно?",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(text="✅ Подтвердить", callback_data="accept_plan"),
                        types.InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_plan")
                    ]
                ]
            ),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        error_msg = f"Ошибка при обработке времени: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "Упс, что-то пошло не так при установке времени.\n"
            "Попробуй еще раз или начни сначала с /plan"
        )

async def callback_accept_plan(callback: types.CallbackQuery, state: FSMContext, db: Database) -> None:
    """Обработка подтверждения плана"""
    try:
        # Получаем данные плана
        data = await state.get_data()
        plan_data = data['plan_data']
        
        # Создаем план
        plan_service = PlanServiceV2(db)
        plan = plan_service.create_plan(
            user_id=data['user_id'],
            data=plan_data
        )
        
        # Очищаем состояние
        await state.clear()
        
        await callback.message.answer(
            "🎉 Отлично, Морти! План создан и готов к выполнению!\n\n"
            "Используй /plans чтобы посмотреть все свои планы."
        )
        await callback.answer()
        
    except Exception as e:
        error_msg = f"Ошибка при сохранении плана: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await callback.message.answer(
            "Упс, что-то пошло не так при сохранении плана.\n"
            "Попробуй создать план заново."
        )
        await callback.answer()

def get_time_block(t: time) -> TimeBlock:
    """Определение временного блока по времени"""
    if time(6, 0) <= t < time(12, 0):
        return TimeBlock.MORNING
    elif time(12, 0) <= t < time(18, 0):
        return TimeBlock.AFTERNOON
    else:
        return TimeBlock.EVENING

def calculate_end_time(start: time, duration_minutes: int) -> time:
    """Расчет времени окончания"""
    dt = datetime.combine(datetime.today(), start)
    end_dt = dt.replace(minute=dt.minute + duration_minutes)
    return end_dt.time()

def format_plan_preview(plan: Dict[str, Any]) -> str:
    """Форматирование плана для предпросмотра"""
    result = [
        f"⏰ {plan['start_time']}-{plan['end_time']} | {plan['title']}",
        f"📝 {plan['description']}" if plan.get('description') else "",
        f"🎯 Приоритет: {plan['priority'].capitalize()}",
        f"⏱ Длительность: {plan['duration_minutes']} минут",
        "\nШаги:"
    ]
    
    for step in plan['steps']:
        result.extend([
            f"\n- {step['title']}",
            f"  {step['description']}" if step.get('description') else "",
            f"  ⏱ {step['duration_minutes']} минут" if step.get('duration_minutes') else ""
        ])
    
    return "\n".join(line for line in result if line)

def register_handlers_v2(router: Router, db: Database) -> None:
    """Регистрация обработчиков v2"""
    router.message.register(
        cmd_plan_v2,
        Command(commands=["plan"]),
        StateFilter(None)
    )
    
    router.message.register(
        process_plan_input,
        StateFilter(PlanStatesV2.WAITING_FOR_PLAN)
    )
    
    router.message.register(
        process_time_input,
        StateFilter(PlanStatesV2.WAITING_FOR_TIME)
    )
    
    router.callback_query.register(
        callback_accept_plan,
        F.data == "accept_plan",
        StateFilter(PlanStatesV2.CONFIRMING_PLAN)
    )
