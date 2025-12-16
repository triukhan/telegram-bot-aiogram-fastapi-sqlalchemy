import re
from datetime import datetime
from logging import Logger
from typing import Iterable

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.models import Subscription


class SubscriptionRepository:
    def __init__(self, async_session: async_sessionmaker, logger: Logger):
        self.__async_session = async_session
        self.logger = logger

    async def get(self, user_id: int) -> Subscription | None:
        async with self.__async_session() as session:
            result = await session.execute(select(Subscription).where(Subscription.user_id == user_id))
            return result.scalar_one_or_none()

    async def get_all(self) -> Iterable[Subscription]:
        async with self.__async_session() as session:
            result = await session.execute(select(Subscription))
            return result.scalars().all()

    async def get_by_order(self, order_reference: str) -> Subscription | None:
        cleaned = re.sub(r'^(WFP-[^_]+).*_WFPREG.*$', r'\1', order_reference)
        async with self.__async_session() as session:
            result = await session.execute(select(Subscription).where(Subscription.order_reference == cleaned))
            return result.scalar_one_or_none()

    async def add(self, user_id: int, order_reference: str, regular_mode: str) -> None:
        async with self.__async_session() as session:
            sub = Subscription(
                user_id=user_id,
                order_reference=order_reference,
                last_payment_date=int(datetime.now().timestamp()),
                payment_period=regular_mode
            )
            session.add(sub)
            await session.commit()
            self.logger.info(f'subscription added for user <{user_id}> | order: {order_reference}')

    async def remove(self, user_id: int) -> None:
        async with self.__async_session() as session:
            await session.execute(delete(Subscription).where(Subscription.user_id == user_id))
            await session.commit()
            self.logger.info(f'subscription removed for user <{user_id}>')

    async def update(self, user_id: int, fields: dict) -> None:
        if not fields:
            return

        async with self.__async_session() as session:
            await session.execute(update(Subscription).where(Subscription.user_id == user_id).values(**fields))
            await session.commit()
            self.logger.info(f'subscription with user_id <{user_id}> was updated with fields: {fields}')
