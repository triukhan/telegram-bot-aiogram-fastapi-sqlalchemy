from logging import Logger
from typing import Iterable

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.models import User


class UserRepository:
    def __init__(self, async_session: async_sessionmaker, logger: Logger):
        self.__async_session = async_session
        self.logger = logger

    async def get(self, user_id: int) -> User | None:
        async with self.__async_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    async def get_all(self) -> Iterable[User]:
        async with self.__async_session() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def get_admins(self) -> Iterable[User]:
        async with self.__async_session() as session:
            result = await session.execute(select(User).where(User.is_admin))
            return result.scalars().all()

    async def add(self, user_id: int) -> User:
        async with self.__async_session() as session:
            async with session.begin():
                user = await session.merge(User(id=user_id))
                return user
