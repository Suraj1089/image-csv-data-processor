# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Generator, AsyncGenerator


engine = create_async_engine(DATABASE_URL, echo=False)


async def get_db() -> AsyncGenerator:
    async with AsyncSession(engine) as session:
        yield session

