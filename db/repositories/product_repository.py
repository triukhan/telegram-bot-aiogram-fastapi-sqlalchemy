from logging import Logger
from typing import Iterable

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.models import Product
from telegram.utils import ProductStatus


class ProductRepository:
    def __init__(self, async_session: async_sessionmaker, logger: Logger):
        self.__async_session = async_session
        self.logger = logger

    async def get(self, product_id: int) -> Product | None:
        async with self.__async_session() as session:
            result = await session.execute(select(Product).where(Product.id == product_id))
            return result.scalar_one_or_none()

    async def get_all(self) -> Iterable[Product]:
        async with self.__async_session() as session:
            result = await session.execute(select(Product))
            return result.scalars().all()

    async def get_by_name(self, product_name: str) -> Product | None:
        async with self.__async_session() as session:
            result = await session.execute(select(Product).where(Product.name == product_name))
            return result.scalar_one_or_none()

    async def add(self, name: str, price: int, description: str, link: str, status: ProductStatus = ProductStatus.ACTIVE) -> None:
        async with self.__async_session() as session:
            sub = Product(name=name, price=price, description=description, link=link, status=status)
            session.add(sub)
            await session.commit()
            self.logger.info(f'product <{name}> was added')

    async def remove(self, product_id: int) -> None:
        async with self.__async_session() as session:
            await session.execute(delete(Product).where(Product.id == product_id))
            await session.commit()
            self.logger.info(f'product <{product_id}> was removed')

    async def change_status(self, product_id: int, state: int) -> None:
        async with self.__async_session() as session:
            await session.execute(update(Product).where(Product.id == product_id).values(status=state))
            await session.commit()
            self.logger.info(f'state of product <{product_id}> was changed to <{state}>')

    async def update(self, product_id: int, field: str, value) -> None:
        if not hasattr(Product, field):
            raise ValueError(f'Invalid field: {field}')

        async with self.__async_session() as session:
            await session.execute(update(Product).where(Product.id == product_id).values({field: value}))
            await session.commit()
            self.logger.info(f'product <{product_id}> was update with field <{field}> value <{value}>')
