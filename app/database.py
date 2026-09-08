from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated
from fastapi import Depends

from app.config import settings


engine = create_async_engine(settings.db_url)
session_local = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

async def get_connection_db():
    async with session_local() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_connection_db)]

