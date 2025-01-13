"""Premium Feature Handlers for PlanD Bot"""

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from src.services.premium.premium_service import PremiumService
from src.database.models_v3 import InteractionStyle, CalendarType, PremiumFeature

class PremiumStates(StatesGroup):
    """Состояния для премиум функций"""
    WAITING_FOR_STYLE = State()
    WAITING_FOR_CALENDAR = State()
    WAITING_FOR_GIFT_TYPE = State()
    WAITING_FOR_GIFT_AMOUNT = State()
    WAITING_FOR_GIFT_MESSAGE = State()

async def cmd_premium(message: types.Message, premium_service: PremiumService):
    """Показать премиум статус и доступные функции"""
    profile = await premium_service.get_or_create_profile(message.from_user.id)
    
    if profile.premium_until:
        text = f"""
🌟 У вас активна премиум подписка!
Дата окончания: {profile.premium_until.strftime('%Y-%m-%d')}

💰 Ваши коины: {profile.coins}

Доступные функции:
- 📅 Синхронизация календарей
- 🎨 Кастомные стили общения
- 🎁 Премиум стикеры
- 🎯 Расширенные функции AI
        """
    else:
        text = f"""
✨ Откройте для себя премиум возможности!

💰 Ваши коины: {profile.coins}

Премиум включает:
- 📅 Синхронизация с календарями
- 🎨 Уникальные стили общения
- 🎁 Эксклюзивные стикеры
- 🎯 Продвинутый AI

Цена: 1000 коинов/месяц
        """
    
    keyboard = types.InlineKeyboardMarkup()
    
    if not profile.premium_until:
        keyboard.add(types.InlineKeyboardButton(
            "Купить премиум",
            callback_data="premium_buy"
        ))
    
    keyboard.add(
        types.InlineKeyboardButton(
            "Стили общения",
            callback_data="premium_styles"
        ),
        types.InlineKeyboardButton(
            "Календари",
            callback_data="premium_calendar"
        )
    )
    
    keyboard.add(
        types.InlineKeyboardButton(
            "Стикеры",
            callback_data="premium_stickers"
        ),
        types.InlineKeyboardButton(
            "Подарки",
            callback_data="premium_gifts"
        )
    )
    
    await message.answer(text, reply_markup=keyboard)

async def callback_premium_buy(
    callback: types.CallbackQuery,
    premium_service: PremiumService
):
    """Покупка премиум подписки"""
    if await premium_service.spend_coins(
        callback.from_user.id,
        1000,
        "Premium subscription (1 month)"
    ):
        await premium_service.add_premium_days(callback.from_user.id, 30)
        await callback.answer("🌟 Премиум активирован на 30 дней!")
        await cmd_premium(callback.message, premium_service)
    else:
        await callback.answer(
            "Недостаточно коинов! Заработайте их, выполняя задачи.",
            show_alert=True
        )

async def callback_premium_styles(
    callback: types.CallbackQuery,
    state: FSMContext,
    premium_service: PremiumService
):
    """Выбор стиля общения"""
    profile = await premium_service.get_or_create_profile(callback.from_user.id)
    
    if not profile.premium_until and profile.interaction_style != InteractionStyle.RICK:
        await callback.answer(
            "Требуется премиум для смены стиля!",
            show_alert=True
        )
        return
        
    keyboard = types.InlineKeyboardMarkup()
    
    for style in InteractionStyle:
        if style == profile.interaction_style:
            text = f"✓ {style.value.capitalize()}"
        else:
            text = style.value.capitalize()
        keyboard.add(types.InlineKeyboardButton(
            text,
            callback_data=f"style_{style.value}"
        ))
    
    await callback.message.edit_text(
        "Выберите стиль общения:",
        reply_markup=keyboard
    )
    
async def callback_style_select(
    callback: types.CallbackQuery,
    premium_service: PremiumService
):
    """Установка выбранного стиля"""
    style_name = callback.data.split('_')[1]
    style = InteractionStyle(style_name)
    
    try:
        await premium_service.update_interaction_style(
            callback.from_user.id,
            style
        )
        await callback.answer(f"Установлен стиль: {style.value}")
        await cmd_premium(callback.message, premium_service)
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)

async def callback_premium_calendar(
    callback: types.CallbackQuery,
    premium_service: PremiumService
):
    """Управление календарями"""
    if not await premium_service.check_premium_feature(
        callback.from_user.id,
        PremiumFeature.CALENDAR_SYNC
    ):
        await callback.answer(
            "Требуется премиум для синхронизации календарей!",
            show_alert=True
        )
        return
        
    keyboard = types.InlineKeyboardMarkup()
    
    for cal_type in CalendarType:
        keyboard.add(types.InlineKeyboardButton(
            f"Подключить {cal_type.value}",
            callback_data=f"calendar_{cal_type.value}"
        ))
    
    await callback.message.edit_text(
        "Выберите календарь для подключения:",
        reply_markup=keyboard
    )

async def callback_calendar_connect(
    callback: types.CallbackQuery,
    premium_service: PremiumService
):
    """Подключение календаря"""
    cal_type = CalendarType(callback.data.split('_')[1])
    
    # Здесь должна быть логика OAuth2 для выбранного календаря
    # Пока просто заглушка
    await callback.answer(
        f"Подключение {cal_type.value} будет доступно скоро!",
        show_alert=True
    )

async def callback_premium_stickers(
    callback: types.CallbackQuery,
    premium_service: PremiumService
):
    """Просмотр доступных стикерпаков"""
    packs = await premium_service.get_available_sticker_packs(
        callback.from_user.id
    )
    
    if not packs:
        await callback.answer(
            "Стикерпаки пока недоступны!",
            show_alert=True
        )
        return
        
    keyboard = types.InlineKeyboardMarkup()
    
    for pack in packs:
        keyboard.add(types.InlineKeyboardButton(
            f"{pack.name} ({pack.price} коинов)",
            callback_data=f"sticker_pack_{pack.id}"
        ))
    
    await callback.message.edit_text(
        "Доступные стикерпаки:",
        reply_markup=keyboard
    )

async def callback_sticker_pack_buy(
    callback: types.CallbackQuery,
    premium_service: PremiumService
):
    """Покупка стикерпака"""
    pack_id = int(callback.data.split('_')[2])
    
    try:
        await premium_service.purchase_sticker_pack(
            callback.from_user.id,
            pack_id
        )
        await callback.answer("Стикерпак куплен!")
        await cmd_premium(callback.message, premium_service)
    except ValueError as e:
        await callback.answer(str(e), show_alert=True)

async def callback_premium_gifts(
    callback: types.CallbackQuery,
    state: FSMContext
):
    """Отправка подарков"""
    keyboard = types.InlineKeyboardMarkup()
    
    keyboard.add(
        types.InlineKeyboardButton(
            "Коины",
            callback_data="gift_coins"
        ),
        types.InlineKeyboardButton(
            "Стикерпак",
            callback_data="gift_sticker_pack"
        )
    )
    
    keyboard.add(
        types.InlineKeyboardButton(
            "Премиум",
            callback_data="gift_premium"
        )
    )
    
    await callback.message.edit_text(
        "Выберите тип подарка:",
        reply_markup=keyboard
    )
    await PremiumStates.WAITING_FOR_GIFT_TYPE.set()

async def process_gift_type(
    callback: types.CallbackQuery,
    state: FSMContext
):
    """Обработка выбора типа подарка"""
    gift_type = callback.data.split('_')[1]
    await state.update_data(gift_type=gift_type)
    
    await callback.message.edit_text(
        "Введите количество (коинов/дней):"
    )
    await PremiumStates.WAITING_FOR_GIFT_AMOUNT.set()

async def process_gift_amount(
    message: types.Message,
    state: FSMContext
):
    """Обработка количества подарка"""
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        await message.answer("Пожалуйста, введите положительное число!")
        return
        
    await state.update_data(amount=amount)
    
    await message.answer(
        "Введите сообщение к подарку (или /skip для пропуска):"
    )
    await PremiumStates.WAITING_FOR_GIFT_MESSAGE.set()

async def process_gift_message(
    message: types.Message,
    state: FSMContext,
    premium_service: PremiumService
):
    """Обработка сообщения к подарку"""
    if message.text == '/skip':
        message_text = None
    else:
        message_text = message.text
        
    data = await state.get_data()
    
    try:
        await premium_service.send_gift(
            message.from_user.id,
            message.chat.id,  # В реальности нужно будет указать ID получателя
            data['gift_type'],
            amount=data['amount'],
            message=message_text
        )
        await message.answer("Подарок отправлен! 🎁")
    except ValueError as e:
        await message.answer(str(e))
        
    await state.finish()

def register_premium_handlers(dp):
    """Регистрация обработчиков премиум функций"""
    dp.register_message_handler(cmd_premium, commands=['premium'])
    
    dp.register_callback_query_handler(
        callback_premium_buy,
        lambda c: c.data == 'premium_buy'
    )
    
    dp.register_callback_query_handler(
        callback_premium_styles,
        lambda c: c.data == 'premium_styles'
    )
    
    dp.register_callback_query_handler(
        callback_style_select,
        lambda c: c.data.startswith('style_')
    )
    
    dp.register_callback_query_handler(
        callback_premium_calendar,
        lambda c: c.data == 'premium_calendar'
    )
    
    dp.register_callback_query_handler(
        callback_calendar_connect,
        lambda c: c.data.startswith('calendar_')
    )
    
    dp.register_callback_query_handler(
        callback_premium_stickers,
        lambda c: c.data == 'premium_stickers'
    )
    
    dp.register_callback_query_handler(
        callback_sticker_pack_buy,
        lambda c: c.data.startswith('sticker_pack_')
    )
    
    dp.register_callback_query_handler(
        callback_premium_gifts,
        lambda c: c.data == 'premium_gifts'
    )
    
    dp.register_callback_query_handler(
        process_gift_type,
        lambda c: c.data.startswith('gift_'),
        state=PremiumStates.WAITING_FOR_GIFT_TYPE
    )
    
    dp.register_message_handler(
        process_gift_amount,
        state=PremiumStates.WAITING_FOR_GIFT_AMOUNT
    )
    
    dp.register_message_handler(
        process_gift_message,
        state=PremiumStates.WAITING_FOR_GIFT_MESSAGE
    )
