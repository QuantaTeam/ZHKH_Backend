import typing as tp

import fastapi
from sqlalchemy.ext import asyncio as aorm

from sarah import deps
from sarah.anomaly import filters

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
    applications = await filters.get_close_wo_completion_first(db=db, log=log)
    return applications
