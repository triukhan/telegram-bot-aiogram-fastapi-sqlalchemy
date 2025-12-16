from logging import Logger
from typing import Iterable

from sqlalchemy import select, delete, update, and_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.models import SupportChat


class SupportChatRepository:
    def __init__(self, async_session: async_sessionmaker, logger: Logger):
        self.__async_session = async_session
        self.logger = logger

    async def get(self, user_id: int) -> SupportChat | None:
        async with self.__async_session() as session:
            result = await session.execute(select(SupportChat).where(SupportChat.user_id == user_id))
            return result.scalar_one_or_none()

    async def get_all(self) -> Iterable[SupportChat]:
        async with self.__async_session() as session:
            result = await session.execute(select(SupportChat))
            return result.scalars().all()

    async def get_by_admin(self, admin_id: int) -> SupportChat | None:
        async with self.__async_session() as session:
            stmt = select(SupportChat).where(and_(SupportChat.admin_id == admin_id, SupportChat.is_active.is_(True)))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> SupportChat | None:
        async with self.__async_session() as session:
            stmt = select(SupportChat).where(and_(SupportChat.user_id == user_id, SupportChat.is_active.is_(True)))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def add(self, user_id: int) -> None:
        async with self.__async_session() as session:
            stmt = insert(SupportChat).values(user_id=user_id, is_active=True).on_conflict_do_update(
                index_elements=[SupportChat.user_id], set_={'is_active': True, 'admin_id': None}
            )
            await session.execute(stmt)
            await session.commit()
            self.logger.info(f'new chat with user <{user_id}> was added')

    async def remove(self, user_id: int) -> None:
        async with self.__async_session() as session:
            await session.execute(delete(SupportChat).where(SupportChat.user_id == user_id))
            await session.commit()
            self.logger.info(f'chat with user <{user_id}> was removed')

    async def assign_admin(self, user_id: int, admin_id: int) -> None:
        async with self.__async_session() as session:
            stmt = (update(SupportChat).where(SupportChat.user_id == user_id).values(admin_id=admin_id, is_active=True))
            await session.execute(stmt)
            await session.commit()
            self.logger.info(f'admin <{admin_id}> was assigned to chat with user <{user_id}>')

    async def pause(self, user_id: int) -> None:
        async with self.__async_session() as session:
            stmt = (update(SupportChat).where(SupportChat.user_id == user_id).values(is_active=False, admin_id=None))
            await session.execute(stmt)
            await session.commit()
            self.logger.info(f'chat with user <{user_id}> was paused')
