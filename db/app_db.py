import os
from typing import Iterable

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db.models import BaseModel, Order, Product
from db.repositories.order_repository import OrderRepository
from db.repositories.product_repository import ProductRepository
from db.repositories.subscription_repository import SubscriptionRepository
from db.repositories.support_chat_repository import SupportChatRepository
from db.repositories.user_repository import UserRepository
from utils import get_logger

load_dotenv()
POSTGRES_DSN = os.getenv('POSTGRES_DSN')


class AppDB:
    def __init__(self):
        self.__engine = create_async_engine(POSTGRES_DSN, pool_size=10, max_overflow=20)
        self.__async_session = async_sessionmaker(self.__engine, expire_on_commit=False, autoflush=False)
        self.logger = get_logger('AppDB')
        self.users = UserRepository(self.__async_session, self.logger)
        self.products = ProductRepository(self.__async_session, self.logger)
        self.orders = OrderRepository(self.__async_session, self.logger)
        self.subscriptions = SubscriptionRepository(self.__async_session, self.logger)
        self.support_chats = SupportChatRepository(self.__async_session, self.logger)

    async def init_models(self) -> None:
        async with self.__engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    async def get_user_ids_by_product_id(self, product_id: int) -> Iterable[int]:
        async with self.__async_session() as session:
            result = await session.execute(select(Order.user_id).where(Order.product_id == product_id))
            return result.scalars().all()

    async def get_orders_with_products(self, user_id: int):
        async with self.__async_session() as session:
            result = await session.execute(
                select(Order, Product).join(Product, Order.product_id == Product.id).where(Order.user_id == user_id)
            )
            return result.all()
