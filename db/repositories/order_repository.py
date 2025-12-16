from logging import Logger
from typing import Iterable

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.models import Order


class OrderRepository:
    def __init__(self, async_session: async_sessionmaker, logger: Logger):
        self.__async_session = async_session
        self.logger = logger

    async def get(self, order_reference: int) -> Order | None:
        async with self.__async_session() as session:
            result = await session.execute(select(Order).where(Order.wfp_order_reference == order_reference))
            return result.scalar_one_or_none()

    async def get_all(self) -> Iterable[Order]:
        async with self.__async_session() as session:
            result = await session.execute(select(Order))
            return result.scalars().all()

    async def get_by_user(self, user_id: int) -> Iterable[Order]:
        async with self.__async_session() as session:
            result = await session.execute(select(Order).where(Order.user_id == user_id))
            return result.scalars().all()

    async def add(self, user_id: int, product_id: int, order_reference: str) -> None:
        async with self.__async_session() as session:
            stmt = insert(Order).values(
                user_id=user_id, product_id=product_id, wfp_order_reference=order_reference,
            ).on_conflict_do_update(
                index_elements=[Order.user_id, Order.product_id], set_={'wfp_order_reference': order_reference}
            )
            await session.execute(stmt)
            await session.commit()
            self.logger.info(f'order <{order_reference}> for user <{user_id}> added')

    async def remove(self, order_reference: str) -> None:
        async with self.__async_session() as session:
            result = await session.execute(
                delete(Order).where(Order.wfp_order_reference == order_reference).returning(Order.purchased_at)
            )
            await session.commit()

            if not result.fetchall():
                self.logger.warning(f'order <{order_reference}> not found in db')
            else:
                self.logger.info(f'order <{order_reference}> removed from db')
