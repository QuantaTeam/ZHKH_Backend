import typing

import fastapi
import sqlalchemy
from sqlalchemy.ext import asyncio as aorm

from sarah import deps

router: fastapi.APIRouter = fastapi.APIRouter()


@router.get(
    "/anomalies",
    summary="Get multiple applications",
)
async def multi_application(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
) -> typing.Any:
    query = await db.execute(
        sqlalchemy.text(
            "select id, geo_coordinates from application where geo_coordinates is not NULL and is_anomaly = true"
        )
    )
    applications = query.mappings().all()
    if applications is None or len(applications) == 0:
        raise fastapi.HTTPException(
            404, "Either no anomalies found or they haven't been geotagged yet."
        )
    return applications


@router.get(
    "/{application_id}",
    summary="Get one application",
)
async def one_application(
    *,
    application_id: int = fastapi.Query(...),
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
) -> typing.Any:
    query = await db.execute(
        sqlalchemy.text(
            "select * from application where application.id = :application_id"
        ).bindparams(application_id=application_id)
    )
    application = query.mappings().all()
    if application is None or len(application) == 0:
        raise fastapi.HTTPException(
            404, f"Application with {application_id} id not found."
        )
    return application[0]
