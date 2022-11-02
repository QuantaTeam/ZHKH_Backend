import asyncio as aio
import typing as tp

import fastapi
from sqlalchemy.ext import asyncio as aorm

from sarah import deps
from sarah.anomaly import filters
from sarah.anomaly import db as db_queries

is_anomaly_update_started: bool = False
is_async_anomaly_update_started: bool = False

router: fastapi.APIRouter = fastapi.APIRouter()

@router.get(
    "/",
    summary="Get anomalies",
)
async def get_anomalies(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    multi: deps.Multi = fastapi.Depends(),
) -> tp.Any:
    applications = await filters.get_close_wo_completion_second(db=db, log=log)
    log.msg(len(applications))
    return applications


@router.post(
    "/async-update",
    summary="[NOT WORKING] Update async anomalies",
)
async def update_async_anomalies(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    multi: deps.Multi = fastapi.Depends(),
) -> tp.Any:
    global is_async_anomaly_update_started

    if is_async_anomaly_update_started:
        return False
    is_async_anomaly_update_started = True
    try:
        rules = ["first", "second", "third", "fourth", "fifth"]

        async def _update_anomalies(rule: str, db: aorm.AsyncSession, log: tp.Any):
            log.msg(rule)
            filter_func = getattr(filters, f"get_close_wo_completion_{rule}")
            applications = await filter_func(db=db, log=log)
            log.msg(len(applications))
            await db_queries.update_applications_is_anomaly(ids=[application["id"] for application in applications], db=db, log=log)

        tasks = []
        for rule in rules:
            tasks.append(
                _update_anomalies(rule, db, log)
            )
        
        result = await aio.gather(*tasks, return_exceptions=True)
        log.msg(result)
        
    except Exception:
        pass
    finally:
        is_async_anomaly_update_started = False
    return True


@router.post(
    "/update",
    summary="Update anomalies",
)
async def update_anomalies(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    multi: deps.Multi = fastapi.Depends(),
) -> tp.Any:
    global is_anomaly_update_started

    if is_anomaly_update_started:
        return False
    is_anomaly_update_started = True
    try:
        rules = ["first", "second", "third", "fourth", "fifth"]

        for rule in rules:
            filter_func = getattr(filters, f"get_close_wo_completion_{rule}")
            applications = await filter_func(db=db, log=log)
            log.msg(len(applications))
            await db_queries.update_applications_is_anomaly(ids=[application["id"] for application in applications], db=db, log=log)
        
    except Exception:
        pass
    finally:
        is_anomaly_update_started = False
    return True