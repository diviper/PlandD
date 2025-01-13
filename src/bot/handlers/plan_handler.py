"""План-хендлер в стиле Рика и Морти"""
import logging
import traceback
from datetime import datetime
from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage

from src.database.database import Database
from src.database.models import Plan, PlanStep
from src.services.ai.ai_service import AIService

# Настройка логирования
logger = logging.getLogger(__name__)

# Состояния для создания плана
class PlanStates(StatesGroup):
    """Состояния для работы с планами"""
    WAITING_FOR_PLAN = State()  # Ожидание ввода плана
    CONFIRMING_PLAN = State()   # Подтверждение плана
    EDITING_PLAN = State()      # Редактирование плана

async def cmd_plan(message: types.Message, state: FSMContext, db: Database) -> None:
    """Обработчик команды /plan"""
    try:
        # Очищаем предыдущее состояние
        await state.clear()
        
        # Сохраняем user_id в состоянии
        await state.update_data(user_id=message.from_user.id)
        
        # Устанавливаем состояние ожидания плана
        await state.set_state(PlanStates.WAITING_FOR_PLAN)
        
        # Отправляем приветственное сообщение
        await message.answer(
            "🌀 *Давай составим план, Морти!*\n\n"
            "Расскажи мне, что ты хочешь сделать, а я помогу тебе разбить это на простые шаги!\n\n"
            "_Просто напиши свой план в следующем сообщении_",
            parse_mode="Markdown"
        )
        logger.info(f"Пользователь {message.from_user.id} начал создание плана")
        
    except Exception as e:
        error_msg = f"Ошибка при запуске планирования: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "Упс, Морти! Что-то пошло не так при запуске.\n"
            "Давай попробуем еще раз через пару секунд!",
            parse_mode="Markdown"
        )
        await state.clear()

async def process_plan_input(message: types.Message, state: FSMContext, db: Database):
    """Обработка введенного плана"""
    try:
        # Проверяем состояние
        current_state = await state.get_state()
        if current_state != PlanStates.WAITING_FOR_PLAN:
            await message.answer(
                "Упс, Морти! Кажется, мы потерялись в пространстве-времени.\n"
                "Используй /plan, чтобы начать новый план!"
            )
            await state.clear()
            return

        user_text = message.text
        logger.info(f"Получен текст плана от пользователя {message.from_user.id}: {user_text[:50]}...")
        
        # Отправляем сообщение о начале анализа
        processing_msg = await message.answer(
            "🧠 *Анализирую твой план, Морти...*\n"
            "_Это может занять несколько секунд_", 
            parse_mode="Markdown"
        )
        
        try:
            # Создаем экземпляр AI сервиса
            ai_service = AIService(db)
            logger.info("AI сервис создан, начинаем анализ плана...")
            
            # Анализируем план с помощью AI
            analysis = await ai_service.analyze_plan(user_text)
            if not analysis:
                raise ValueError("Не удалось проанализировать план")
                
            logger.info(f"План успешно проанализирован: {analysis}")
            
            # Получаем user_id из состояния
            data = await state.get_data()
            user_id = data.get('user_id', message.from_user.id)
            
            # Создаем план в базе
            plan = Plan(
                user_id=user_id,
                original_text=user_text,
                created_at=datetime.now(),
                ai_suggestions=analysis.get('suggestions', ''),
                status='pending'
            )
            
            # Добавляем шаги плана
            for step in analysis.get('steps', []):
                plan_step = PlanStep(
                    plan=plan,
                    description=step['description'],
                    estimated_duration=step.get('duration', 30),
                    priority=step.get('priority', 'medium'),
                    status='pending'
                )
                plan.steps.append(plan_step)
            
            # Сохраняем в базу
            logger.info("Сохраняем план в базу данных...")
            plan_id = await db.add_plan(plan)
            logger.info(f"План сохранен с ID: {plan_id}")
            
            # Удаляем сообщение о загрузке
            await processing_msg.delete()
            
            # Формируем ответ в стиле Рика
            response = (
                f"*{analysis.get('title', 'Новый план')}*\n\n"
                f"Вот как я вижу твой план, внучек:\n\n"
            )
            
            for i, step in enumerate(plan.steps, 1):
                response += f"{i}. {step.description} (~{step.estimated_duration} мин)\n"
            
            if analysis.get('suggestions'):
                response += f"\n🧪 *Рекомендации:*\n{analysis['suggestions']}\n"
                
            response += "\nХочешь что-то изменить или *burp* погнали выполнять?"
            
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="🚀 Погнали!", callback_data=f"accept_plan:{plan_id}"),
                    types.InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_plan:{plan_id}")
                ]
            ])
            
            logger.info("Отправляем ответ пользователю...")
            await message.reply(response, reply_markup=keyboard, parse_mode="Markdown")
            await state.set_state(PlanStates.CONFIRMING_PLAN)
            await state.update_data(plan_id=plan_id)
            logger.info("Ответ отправлен успешно")
        
        except Exception as e:
            logger.error(f"Ошибка при анализе плана: {str(e)}")
            await processing_msg.edit_text(
                "Уупс, Морти! *burp* Что-то пошло не так при анализе плана.\n"
                "Давай попробуем еще раз! Используй /plan",
                parse_mode="Markdown"
            )
            await state.clear()

    except Exception as e:
        error_msg = f"Ошибка при обработке плана: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        await message.answer(
            "Уупс, Морти! *burp* Произошла квантовая аномалия!\n"
            "Давай попробуем еще раз через /plan",
            parse_mode="Markdown"
        )
        await state.clear()

async def callback_accept_plan(callback_query: types.CallbackQuery, state: FSMContext, db: Database):
    """Обработка подтверждения плана"""
    try:
        plan_id = int(callback_query.data.split(':')[1])
        await callback_query.message.edit_text(
            "Отличный выбор, Морти! *burp* \n"
            "Теперь держись крепче, мы отправляемся в приключение по выполнению твоего плана!\n"
            "Я буду следить за тобой, как дедуля за внучком! 👴🔬",
            parse_mode="Markdown"
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при подтверждении плана: {str(e)}")
        await callback_query.message.edit_text(
            "Уупс, что-то пошло не так при подтверждении плана!\n"
            "Попробуй создать новый план через /plan"
        )
        await state.clear()

async def callback_edit_plan(callback_query: types.CallbackQuery, state: FSMContext, db: Database):
    """Обработка редактирования плана"""
    try:
        plan_id = int(callback_query.data.split(':')[1])
        await callback_query.message.edit_text(
            "Ох, Морти, опять все переделывать? *burp*\n"
            "Ну давай, говори что не так, только по существу!",
            parse_mode="Markdown"
        )
        await state.set_state(PlanStates.EDITING_PLAN)
        await state.update_data(plan_id=plan_id)
    except Exception as e:
        logger.error(f"Ошибка при редактировании плана: {str(e)}")
        await callback_query.message.edit_text(
            "Уупс, что-то пошло не так при редактировании плана!\n"
            "Попробуй создать новый план через /plan"
        )
        await state.clear()

def register_handlers(dp: Router, db: Database):
    """Регистрация обработчиков планов"""
    # Создаем роутер для планов
    plan_router = Router(name="plan_router")
    
    # Команды
    plan_router.message.register(cmd_plan, Command("plan"))
    
    # Обработчики состояний
    plan_router.message.register(
        process_plan_input,
        StateFilter(PlanStates.WAITING_FOR_PLAN)
    )
    
    # Колбэки
    plan_router.callback_query.register(
        callback_accept_plan,
        F.data.startswith("accept_plan:")
    )
    plan_router.callback_query.register(
        callback_edit_plan,
        F.data.startswith("edit_plan:")
    )
    
    # Подключаем роутер к основному роутеру
    dp.include_router(plan_router)
