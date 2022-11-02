import itertools as it
import time
import typing as tp

import fastapi
import sqlalchemy
from sqlalchemy.ext import asyncio as aorm

from sarah import deps
from sarah.anomaly import filters


def update_anomalies(
    filter_func: tp.Callable,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger)
):
    log.msg("hey")
        applications = filter_func(db=db, log=log)
        update_applications_is_anomaly([application["id"] for application in applications])
    return


def main():
    rules = ["first", "second", "third", "fourth", "fifth"]

    while True:
        for rule in rules:
            filter_func = getattr(filters, f"get_close_wo_completion_{rule}")
            update_anomalies(filter_func)
        time.sleep(60)


if __name__ == "__main__":
    main()
