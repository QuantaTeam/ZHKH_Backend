import math
import typing

import fastapi
import sqlalchemy
from sqlalchemy.ext import asyncio as aorm

from sarah import deps

router: fastapi.APIRouter = fastapi.APIRouter()


@router.get(
    "/",
    summary="Get multiple applications",
)
async def get_orders(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
    multi: deps.Multi = fastapi.Depends(),
    is_anomaly: bool | None = fastapi.Query(default=None),
    # Наименование категории дефекта
    defect_category_name: str | None = fastapi.Query(default=None),
    # Вид выполненных работ
    type_of_work_performed: str | None = fastapi.Query(default=None),
    # Код района
    district_code: str | None = fastapi.Query(default=None),
) -> typing.Any:
    extra_conditions = ""
    sql_where_init = False
    if defect_category_name:
        extra_conditions += (
            ' where "Наименование категории дефекта" = :defect_category_name '
        )
    if type_of_work_performed:
        extra_conditions += ' where "Вид выполненных работ" = :type_of_work_performed '
    if district_code:
        extra_conditions += ' where "Код района" = :district_code '
    base = sqlalchemy.text(
        "select * from application "
        + extra_conditions
        + f" limit {multi.limit} offset {multi.offset}"
    )
    base_count = sqlalchemy.text(
        "select count(*) from application "
        + extra_conditions
        + f" limit {multi.limit} offset {multi.offset}"
    )
    params = {}
    if defect_category_name:
        params["defect_category_name"] = defect_category_name
    if type_of_work_performed:
        params["type_of_work_performed"] = type_of_work_performed
    if district_code:
        params["district_code"] = district_code

    print(params)
    base = base.bindparams(**params)
    print(base)
    base_count = base_count.bindparams(**params)

    applications_res = await db.execute(base)
    applications = applications_res.mappings().all()
    applications_count_res = await db.execute(base_count)
    applications_count = applications_count_res.scalar_one()
    count_pages = math.ceil(applications_count / multi.limit)
    return {"result": applications, "count_pages": count_pages}


@router.get(
    "/anomalies",
    summary="Get multiple applications",
)
async def anomalies(
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
