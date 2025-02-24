# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from sqlalchemy.ext.asyncio import async_sessionmaker

engine = create_async_engine(DATABASE_URL, echo=True)


async def get_db() -> Generator:
    async with AsyncSession(engine) as session:
        yield session

