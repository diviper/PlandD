"""План-хендлер в стиле Рика и Морти"""
import logging
import traceback
from datetime import datetime
from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from src.database.database import Database
from src.database.models import Plan, PlanStep
from src.services.ai.ai_service import AIService

logger = logging.getLogger(__name__)

class PlanStates(StatesGroup):
    """Состояния для создания плана"""
    WAITING_FOR_PLAN = State()
    CONFIRMING_PLAN = State()
    EDITING_PLAN = State()

# Создаем роутер для планов
router = Router(name="plans")

async def cmd_plan(message: types.Message, state: FSMContext) -> SendMessage:
    """
    Handle /plan command
    """
    try:
        await state.set_state(PlanStates.WAITING_FOR_PLAN)
        text = (
            "Отлично, Морти! *burp* 🥒\n\n"
            "Расскажи мне о своем плане, и я помогу тебе его оптимизировать!\n"
            "Можешь описать все подробно, я пойму."
        )
        return SendMessage(chat_id=message.chat.id, text=text)

    except Exception as e:
        error_msg = f"Ошибка при обработке команды /plan: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return SendMessage(chat_id=message.chat.id, text=error_msg)

async def process_plan_input(message: types.Message, state: FSMContext, ai_service: AIService, db: Database):
    """Обработка введенного плана"""
    user_text = message.text
    
    # Анализируем план с помощью AI
    analysis = await ai_service.analyze_plan(user_text)
    
    # Создаем план в базе
    plan = Plan(
        user_id=message.from_user.id,
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
            estimated_duration=step['duration'],
            priority=step['priority'],
            status='pending'
        )
        plan.steps.append(plan_step)
    
    # Сохраняем в базу
    plan_id = await db.add_plan(plan)
    
    # Формируем ответ в стиле Рика
    response = (
        f"*Так-так, что тут у нас, Морти?*\n\n"
        f"Вот как я вижу твой план, внучек:\n\n"
    )
    
    for i, step in enumerate(plan.steps, 1):
        response += f"{i}. {step.description} (~{step.estimated_duration} мин)\n"
    
    response += "\nХочешь что-то изменить или *burp* погнали выполнять?"
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🚀 Погнали!", callback_data=f"accept_plan:{plan_id}"),
        types.InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_plan:{plan_id}")
    )
    
    await message.reply(response, reply_markup=keyboard, parse_mode="Markdown")
    await PlanStates.CONFIRMING_PLAN.set()
    await state.update_data(plan_id=plan_id)

async def callback_accept_plan(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка подтверждения плана"""
    plan_id = int(callback_query.data.split(':')[1])
    await callback_query.message.edit_text(
        "Отличный выбор, Морти! *burp* \n"
        "Теперь держись крепче, мы отправляемся в приключение по выполнению твоего плана!\n"
        "Я буду следить за тобой, как дедуля за внучком! 👴🔬",
        parse_mode="Markdown"
    )
    await state.finish()

async def callback_edit_plan(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка редактирования плана"""
    plan_id = int(callback_query.data.split(':')[1])
    await callback_query.message.edit_text(
        "Ох, Морти, опять все переделывать? *burp*\n"
        "Ну давай, говори что не так, только по существу!",
        parse_mode="Markdown"
    )
    await PlanStates.EDITING_PLAN.set()
    await state.update_data(plan_id=plan_id)

def register_handlers(dp: Router):
    """Регистрация обработчиков"""
    # Команды
    router.message.register(cmd_plan, Command("plan"))
    
    # Обработка состояний
    router.message.register(process_plan_input, StateFilter(PlanStates.WAITING_FOR_PLAN))
    
    # Колбэки
    router.callback_query.register(callback_accept_plan, F.data.startswith("accept_plan:"))
    router.callback_query.register(callback_edit_plan, F.data.startswith("edit_plan:"))
    
    # Подключаем роутер к диспетчеру, если он еще не подключен
    if router.parent_router is None:
        dp.include_router(router)
