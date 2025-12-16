from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, DateTime, func, Enum
from sqlalchemy import BigInteger, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from telegram.utils import ProductStatus


class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Subscription(BaseModel):
    __tablename__ = 'subscriptions'

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.id', ondelete='RESTRICT'), primary_key=True
    )
    order_reference: Mapped[str] = mapped_column(Text, nullable=False)
    last_payment_date: Mapped[int] = mapped_column(BigInteger, nullable=False)
    last_reminder_sent: Mapped[int | None] = mapped_column(BigInteger)
    unsuccessful_payment: Mapped[bool] = mapped_column(Boolean, default=False)
    payment_period: Mapped[str] = mapped_column(Text, nullable=False)


class Product(BaseModel):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, name='product_status'),
        default=ProductStatus.ACTIVE,
        nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str] = mapped_column(Text, nullable=False)


class Order(BaseModel):
    __tablename__ = 'orders'

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('products.id', ondelete='CASCADE'), primary_key=True
    )
    purchased_at: Mapped['datetime'] = mapped_column(DateTime, server_default=func.now())
    wfp_order_reference: Mapped[str | None] = mapped_column(Text)


class SupportChat(BaseModel):
    __tablename__ = 'support_chats'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    admin_id: Mapped[int | None] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
