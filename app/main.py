from fastapi import FastAPI 
from app.routes import router
from contextlib import asynccontextmanager
from app.db import engine
from app.models import Base
from app.config import DATABASE_URL
# @asynccontextmanager
async def lifespan(app: FastAPI):
    # don't do this in prod.
    # only for demo and learning 
    # use alembic for migration
    print('Starting app................')
    print('Creating tables.............')
    print(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print('Deleting all the tables')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print('Shutting down the app.......')


app = FastAPI(lifespan=lifespan)

app.include_router(router)

@app.get('/')
def home():
    return {"data": "Home"}