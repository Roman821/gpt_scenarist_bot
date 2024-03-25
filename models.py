from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True, unique=True, nullable=False)
    genre = Column(String)
    character = Column(String)
    setting = Column(String)
    tokens_spent = Column(Integer, nullable=False, default=0)

    history_records = relationship('HistoryRecord', back_populates='user')


class HistoryRecord(Base):

    __tablename__ = 'history_records'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String, nullable=False)
    role = Column(SmallInteger, nullable=False)

    user = relationship('User', back_populates='history_records')
