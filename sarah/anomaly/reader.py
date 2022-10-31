import itertools as it 
import typing as tp

import fastapi
import sqlalchemy
from sqlalchemy.ext import asyncio as aorm

from sarah import deps
from sarah.anomaly import db as db_queries
from sarah.anomaly import filters


def read_anomalies(
    db_query_func: tp.Callable, 
    filter_func: tp.Callable,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    batch_size: int = 10000):
    query_applications = db_query_func(db=db, log=log)
    while query_applications:
        applications = filter_func(db=db, log=log)
        update_applications_is_anomaly([application["id"] for application in applications])
    return
