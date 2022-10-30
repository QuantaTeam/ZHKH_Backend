import math
import typing
from datetime import datetime

import fastapi
import sqlalchemy
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import asyncio as aorm

from sarah import deps

router: fastapi.APIRouter = fastapi.APIRouter()


def apply_where_filters(
    statement: typing.Any, filters: dict[str, list[str] | None]
) -> typing.Any:
    parameter_count = 0
    for column, parameter_value in filters.items():
        if parameter_value:
            parameter_count += 1
            parameter_name = f"user_param_{str(parameter_count)}"
            statement = statement.where(sa.Column(column).in_(parameter_value))
    return statement


def apply_time_filters(
    statement: typing.Any,
    filters: list[tuple[str, datetime | None, str]],
    table_name: str,
) -> typing.Any:
    parameter_count = 0
    for rule in filters:
        column, parameter_value, operator = rule
        parameter_count += 1
        parameter_name = f"user_time_param_{str(parameter_count)}"
        if parameter_value:
            statement = statement.where(
                sa.text(
                    f"{table_name}.{column} {operator} :{parameter_name}"
                ).bindparams(
                    sa.bindparam(
                        parameter_name,
                        value=parameter_value,
                        type_=postgresql.TIMESTAMP(timezone=True),
                    )
                )
            )
    return statement


@router.get(
    "/",
    summary="Get multiple applications",
)
async def get_applications(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
    multi: deps.Multi = fastapi.Depends(),
    is_anomaly: bool | None = fastapi.Query(default=None),
    # Наименование категории дефекта
    defect_category_name: typing.List[str] | None = fastapi.Query(default=None),
    # Вид выполненных работ
    type_of_work_performed: typing.List[str] | None = fastapi.Query(default=None),
    # Код района
    district_code: typing.List[str] | None = fastapi.Query(default=None),
    creation_timestamp_start: datetime | None = fastapi.Query(default=None),
    creation_timestamp_end: datetime | None = fastapi.Query(default=None),
    closure_timestamp_start: datetime | None = fastapi.Query(default=None),
    closure_timestamp_end: datetime | None = fastapi.Query(default=None),
) -> typing.Any:
    filters = {
        "Наименование категории дефекта": defect_category_name,
        "Вид выполненных работ": type_of_work_performed,
        "Код района": district_code,
    }
    time_filters = [
        ("application_creation_timestamp", creation_timestamp_start, ">"),
        ("application_creation_timestamp", creation_timestamp_end, "<"),
        ("application_closure_timestamp", closure_timestamp_start, ">"),
        ("application_closure_timestamp", closure_timestamp_end, "<"),
    ]
    statement = sa.select(sa.text("* from application"))
    statement_count = sa.select(sa.text("count(*) from application"))
    statement = apply_where_filters(statement, filters)
    statement_count = apply_where_filters(statement_count, filters)
    statement = apply_time_filters(statement, time_filters, "application")
    statement_count = apply_time_filters(statement_count, time_filters, "application")

    if is_anomaly is not None:
        statement = statement.where(sa.Column("is_anomaly").__eq__(is_anomaly))
        statement_count = statement_count.where(
            sa.Column("is_anomaly").__eq__(is_anomaly)
        )

    statement = statement.limit(multi.limit).offset(multi.offset)
    res_raw = await db.execute(statement)
    res = res_raw.mappings().all()
    res_count_raw = await db.execute(statement_count)
    res_count = res_count_raw.scalar_one()
    count_pages = math.ceil(res_count / multi.limit)
    return {"res": res, "count_pages": count_pages}


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
    "/meta",
    summary="Get metadata",
)
async def meta(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
) -> typing.Any:
    defect_category_name_query = await db.execute(
        sqlalchemy.text('select distinct "Наименование категории дефекта" from application')
    )
    defect_category_name = defect_category_name_query.scalars().all()

    type_of_work_performed_query = await db.execute(
        sqlalchemy.text('select distinct "Вид выполненных работ" from application')
    )
    type_of_work_performed = type_of_work_performed_query.scalars().all()

    district_code_query = await db.execute(
        sqlalchemy.text('select distinct "Код района" from application')
    )
    district_code = district_code_query.scalars().all()

    return {
        "defect_category_name": defect_category_name,
        "type_of_work_performed": type_of_work_performed,
        "district_code": district_code,
    }


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
