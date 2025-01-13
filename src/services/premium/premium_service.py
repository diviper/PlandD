"""Premium Service for PlanD Bot"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.database.models_v3 import (
    UserProfile, CalendarConnection, CalendarEvent,
    StickerPack, UserStickerPack, CoinTransaction,
    Gift, InteractionStyle, CalendarType, PremiumFeature
)

class PremiumService:
    """Сервис для работы с премиум функциями"""

    def __init__(self, db: Session):
        self.db = db

    # Управление профилем

    async def get_or_create_profile(self, user_id: int) -> UserProfile:
        """Получить или создать профиль пользователя"""
        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

        if not profile:
            profile = UserProfile(
                user_id=user_id,
                coins=100,  # Начальный бонус
                interaction_style=InteractionStyle.RICK
            )
            self.db.add(profile)
            self.db.commit()

        return profile

    async def update_interaction_style(
        self, 
        user_id: int, 
        style: InteractionStyle
    ) -> UserProfile:
        """Обновить стиль взаимодействия"""
        profile = await self.get_or_create_profile(user_id)
        
        if style != InteractionStyle.RICK and not profile.premium_until:
            raise ValueError("Premium required for custom styles")

        profile.interaction_style = style
        self.db.commit()
        return profile

    # Управление коинами

    async def add_coins(
        self, 
        user_id: int, 
        amount: int, 
        description: str
    ) -> CoinTransaction:
        """Начислить коины пользователю"""
        profile = await self.get_or_create_profile(user_id)
        
        transaction = CoinTransaction(
            user_profile_id=profile.id,
            amount=amount,
            description=description
        )
        
        profile.coins += amount
        
        self.db.add(transaction)
        self.db.commit()
        
        return transaction

    async def spend_coins(
        self, 
        user_id: int, 
        amount: int, 
        description: str
    ) -> bool:
        """Потратить коины"""
        profile = await self.get_or_create_profile(user_id)
        
        if profile.coins < amount:
            return False
            
        transaction = CoinTransaction(
            user_profile_id=profile.id,
            amount=-amount,
            description=description
        )
        
        profile.coins -= amount
        
        self.db.add(transaction)
        self.db.commit()
        
        return True

    # Управление календарем

    async def connect_calendar(
        self,
        user_id: int,
        calendar_type: CalendarType,
        access_token: str,
        refresh_token: str,
        calendar_id: str,
        is_primary: bool = False
    ) -> CalendarConnection:
        """Подключить календарь"""
        profile = await self.get_or_create_profile(user_id)
        
        if not profile.premium_until:
            raise ValueError("Premium required for calendar sync")
            
        connection = CalendarConnection(
            user_profile_id=profile.id,
            calendar_type=calendar_type,
            calendar_id=calendar_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires=datetime.utcnow() + timedelta(hours=1),
            is_primary=is_primary
        )
        
        self.db.add(connection)
        self.db.commit()
        
        return connection

    async def sync_calendar_events(
        self,
        user_id: int,
        calendar_id: str,
        events: List[Dict[str, Any]]
    ) -> List[CalendarEvent]:
        """Синхронизировать события календаря"""
        connection = self.db.query(CalendarConnection).filter(
            and_(
                CalendarConnection.calendar_id == calendar_id,
                CalendarConnection.user_profile.has(user_id=user_id)
            )
        ).first()
        
        if not connection:
            raise ValueError("Calendar not found")
            
        new_events = []
        for event_data in events:
            event = CalendarEvent(
                calendar_id=connection.id,
                external_id=event_data['id'],
                title=event_data['title'],
                description=event_data.get('description', ''),
                start_time=event_data['start_time'],
                end_time=event_data['end_time'],
                is_all_day=event_data.get('is_all_day', False),
                is_recurring=event_data.get('is_recurring', False),
                recurrence_rule=event_data.get('recurrence_rule'),
                importance=event_data.get('importance', 3)
            )
            new_events.append(event)
            
        self.db.add_all(new_events)
        self.db.commit()
        
        return new_events

    async def check_calendar_conflicts(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[CalendarEvent]:
        """Проверить конфликты с календарем"""
        return self.db.query(CalendarEvent).join(
            CalendarConnection
        ).join(
            UserProfile
        ).filter(
            and_(
                UserProfile.user_id == user_id,
                or_(
                    and_(
                        CalendarEvent.start_time <= start_time,
                        CalendarEvent.end_time > start_time
                    ),
                    and_(
                        CalendarEvent.start_time < end_time,
                        CalendarEvent.end_time >= end_time
                    )
                )
            )
        ).all()

    # Управление стикерами

    async def get_available_sticker_packs(
        self,
        user_id: int
    ) -> List[StickerPack]:
        """Получить доступные стикерпаки"""
        profile = await self.get_or_create_profile(user_id)
        
        query = self.db.query(StickerPack)
        if not profile.premium_until:
            query = query.filter(StickerPack.is_premium == False)
            
        return query.all()

    async def purchase_sticker_pack(
        self,
        user_id: int,
        pack_id: int
    ) -> Optional[UserStickerPack]:
        """Купить стикерпак"""
        profile = await self.get_or_create_profile(user_id)
        pack = self.db.query(StickerPack).get(pack_id)
        
        if not pack:
            return None
            
        if pack.is_premium and not profile.premium_until:
            raise ValueError("Premium required for this sticker pack")
            
        if not await self.spend_coins(user_id, pack.price, f"Purchase sticker pack: {pack.name}"):
            raise ValueError("Not enough coins")
            
        purchase = UserStickerPack(
            user_profile_id=profile.id,
            sticker_pack_id=pack_id
        )
        
        self.db.add(purchase)
        self.db.commit()
        
        return purchase

    # Управление подарками

    async def send_gift(
        self,
        from_user_id: int,
        to_user_id: int,
        item_type: str,
        item_id: Optional[int] = None,
        amount: Optional[int] = None,
        message: Optional[str] = None,
        is_anonymous: bool = False
    ) -> Gift:
        """Отправить подарок"""
        from_profile = await self.get_or_create_profile(from_user_id)
        to_profile = await self.get_or_create_profile(to_user_id)
        
        # Проверяем стоимость подарка
        cost = 0
        if item_type == 'coins':
            cost = amount
        elif item_type == 'sticker_pack':
            pack = self.db.query(StickerPack).get(item_id)
            if not pack:
                raise ValueError("Sticker pack not found")
            cost = pack.price
        elif item_type == 'premium_days':
            cost = amount * 100  # 100 коинов за день премиума
            
        if not await self.spend_coins(from_user_id, cost, f"Send gift to user {to_user_id}"):
            raise ValueError("Not enough coins")
            
        gift = Gift(
            from_user_id=from_profile.id,
            to_user_id=to_profile.id,
            item_type=item_type,
            item_id=item_id,
            amount=amount,
            message=message,
            is_anonymous=is_anonymous
        )
        
        self.db.add(gift)
        self.db.commit()
        
        # Применяем подарок
        if item_type == 'coins':
            await self.add_coins(to_user_id, amount, f"Gift from user {from_user_id}")
        elif item_type == 'sticker_pack':
            await self.purchase_sticker_pack(to_user_id, item_id)
        elif item_type == 'premium_days':
            await self.add_premium_days(to_user_id, amount)
            
        return gift

    # Управление премиум статусом

    async def add_premium_days(
        self,
        user_id: int,
        days: int
    ) -> UserProfile:
        """Добавить дни премиума"""
        profile = await self.get_or_create_profile(user_id)
        
        if profile.premium_until:
            profile.premium_until += timedelta(days=days)
        else:
            profile.premium_until = datetime.utcnow() + timedelta(days=days)
            
        self.db.commit()
        return profile

    async def check_premium_feature(
        self,
        user_id: int,
        feature: PremiumFeature
    ) -> bool:
        """Проверить доступность премиум функции"""
        profile = await self.get_or_create_profile(user_id)
        
        if not profile.premium_until:
            return False
            
        if profile.premium_until < datetime.utcnow():
            profile.premium_until = None
            self.db.commit()
            return False
            
        return True
