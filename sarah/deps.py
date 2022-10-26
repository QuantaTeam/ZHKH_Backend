import typing
from collections import abc

import fastapi
from sqlalchemy.ext import asyncio

from sarah import db, main


async def logger(request: fastapi.Request) -> typing.Any:
    log = main.logger.bind(
        method=request.method,
        url=request.url,
        query_params=request.query_params,
        path_params=request.path_params,
    )
    return log


async def get_async_db() -> abc.AsyncGenerator[asyncio.AsyncSession, None]:
    async with db.async_session() as session:
        yield session


class Multi:
    def __init__(
        self,
        skip: int = fastapi.Query(0, title="SQL's OFFSET.", ge=0, le=1000000),
        limit: int = fastapi.Query(12, title="SQL's LIMIT.", ge=0, le=50),
    ):
        self.offset = skip
        self.limit = limit
