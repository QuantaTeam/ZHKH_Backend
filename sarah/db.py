import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext import asyncio

from sarah import config

engine = sqlalchemy.create_engine(
    config.settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    future=True,
)  # type: ignore
SessionLocal = orm.sessionmaker(
    autocommit=False, autoflush=True, bind=engine, future=True
)

async_engine = asyncio.create_async_engine(
    config.settings.SQLALCHEMY_DATABASE_URI_ASYNC, pool_pre_ping=True
)
async_session = orm.sessionmaker(
    bind=async_engine,
    class_=asyncio.AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
