from uuid import uuid4

from datetime import datetime, timezone

from sqlalchemy.orm import relationship
from sqlalchemy import DateTime, UUID, Integer, String, Column, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .db import Base, DATABASE_URL



# Таблица Пользователей
class User(Base):
    __tablename__ = 'users'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    # Телеграм Айди
    telegram_id = Column(Integer, nullable=False, unique=True)
    # Телеграм Ник
    user_name = Column(String(100), nullable=True)
    # Дата регистрации
    registered_at = Column(DateTime, default=datetime.now(timezone.utc))
    # Связь с таблицей подписки
    subscriptions = relationship("Subscriptions", back_populates="user", cascade="all, delete",
                                 primaryjoin="User.telegram_id==Subscriptions.telegram_id")
    # Связь платежей
    payments = relationship("Payments", back_populates="user", cascade="all, delete",
                            primaryjoin="User.telegram_id==Payments.telegram_id")

# Таблица подписок
class Subscriptions(Base):
    __tablename__ = 'subscriptions'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    # Телеграм айди для привязки к подписке
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    # Дата покупки
    registered_at = Column(DateTime, default=datetime.now(timezone.utc))
    # Количество дней подписки
    day_count = Column(Integer, nullable=False, default=30)  # По умолчанию 30 дней
    # Число дня
    day = Column(Integer, nullable=False)
    # Число Месяца
    month = Column(Integer, nullable=False)
    # Год
    year = Column(Integer, nullable=False)
    # Связка с Телеграм Айди Пользователя
    user = relationship("User", back_populates="subscriptions",
                        primaryjoin="Subscriptions.telegram_id==User.telegram_id")


# Таблица Платежей
class Payments(Base):
    __tablename__ = 'payments'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    # Телеграм айди для привязки
    telegram_id = Column(Integer, ForeignKey('users.telegram_id'), nullable=False)
    # Дата покупки
    registered_at = Column(DateTime, default=datetime.now(timezone.utc))
    # Количество дней подписки
    day_count = Column(Integer, nullable=False)
    # Внесенная сумма оплаты
    pay_sum = Column(Integer, nullable=False)
    # Число дня
    day = Column(Integer, nullable=False)
    # Число Месяца
    month = Column(Integer, nullable=False)
    # Год
    year = Column(Integer, nullable=False)
    # Связка с Телеграм Айди Пользователя
    user = relationship("User", back_populates="payments",
                        primaryjoin="Payments.telegram_id==User.telegram_id")
