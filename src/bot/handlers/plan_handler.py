"""План-хендлер в стиле Рика и Морти"""
import logging
from datetime import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from src.database.database import Database
from src.database.models import Plan, PlanStep
from src.services.ai.ai_service import AIService

logger = logging.getLogger(__name__)

class PlanStates(StatesGroup):
    """Состояния для создания плана"""
    WAITING_FOR_PLAN = State()
    CONFIRMING_PLAN = State()
    EDITING_PLAN = State()

async def cmd_plan(message: types.Message, state: FSMContext):
    """Обработчик команды /plan"""
    await message.reply(
        "Воу-воу, *burp* какие планы на сегодня?\n"
        "Давай, Морти, выкладывай свои дела, а я *burp* разложу их по полочкам!\n"
        "Только без этой занудной ерунды, ок?",
        parse_mode="Markdown"
    )
    await PlanStates.WAITING_FOR_PLAN.set()

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

def register_handlers(dp):
    """Регистрация обработчиков"""
    dp.register_message_handler(cmd_plan, commands=['plan'])
    dp.register_message_handler(process_plan_input, state=PlanStates.WAITING_FOR_PLAN)
    dp.register_callback_query_handler(callback_accept_plan, lambda c: c.data.startswith('accept_plan:'), state=PlanStates.CONFIRMING_PLAN)
    dp.register_callback_query_handler(callback_edit_plan, lambda c: c.data.startswith('edit_plan:'), state=PlanStates.CONFIRMING_PLAN)
