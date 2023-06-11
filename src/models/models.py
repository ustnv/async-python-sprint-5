import uuid

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, relationship  # type: ignore

from db.db import get_session

Base = declarative_base()


class File(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(100), nullable=False)
    path = Column(String(255), nullable=False, unique=True)
    size = Column(Integer(), nullable=False)
    is_downloadable = Column(Boolean(), default=True, nullable=False)

    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', backref='files')


class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)
