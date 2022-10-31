import math
import typing
from datetime import datetime

import fastapi
import sqlalchemy
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import asyncio as aorm

from fastapi_cache.decorator import cache

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
)
@cache(expire=60)
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
    # Наименование района
    district_name: list[str] | None = fastapi.Query(default=None),
    # Наименование управляющей компани
    name_of_the_management_company: list[str] | None = fastapi.Query(default=None),
    # Наименование обслуживавшей орган
    name_of_the_service_organization: list[str] | None = fastapi.Query(default=None),
    # Наименование источника поступлен
    source_name: list[str] | None = fastapi.Query(default=None),
    # Оценка качества выполнения работ
    quality_evaluation: list[str] | None = fastapi.Query(default=None),
    creation_timestamp_start: datetime | None = fastapi.Query(default=None),
    creation_timestamp_end: datetime | None = fastapi.Query(default=None),
    closure_timestamp_start: datetime | None = fastapi.Query(default=None),
    closure_timestamp_end: datetime | None = fastapi.Query(default=None),
    query: str | None = fastapi.Query(default=None),
) -> typing.Any:
    filters = {
        "Наименование категории дефекта": defect_category_name,
        "Вид выполненных работ": type_of_work_performed,
        "Код района": district_code,
        "Наименование района": district_name,
        "Наименование управляющей компани": name_of_the_management_company,
        "Наименование обслуживавшей орган": name_of_the_service_organization,
        "Наименование источника поступлен": source_name,
        "Оценка качества выполнения работ": quality_evaluation,
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

    if query is not None and len(query) > 0:
        statement = statement.where(
            sa.text(f"\"Описание\" LIKE '%' || :query_param || '%'").bindparams(
                sa.bindparam(
                    "query_param",
                    value=query,
                )
            )
        )
        statement_count = statement_count.where(
            sa.text(f"\"Описание\" LIKE '%' || :query_param || '%'").bindparams(
                sa.bindparam(
                    "query_param",
                    value=query,
                )
            )
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
)
@cache(expire=60)
async def anomalies(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
) -> typing.Any:
    query = await db.execute(
        sqlalchemy.text(
            'select id, geo_coordinates, "Наименование дефекта" from application where geo_coordinates is not NULL and is_anomaly = true'
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
@cache(expire=60)
async def meta(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
) -> typing.Any:
    filters = {
        "Наименование категории дефекта": "defect_category_name",
        "Вид выполненных работ": "type_of_work_performed",
        "Код района": "district_code",
        "Наименование района": "district_name",
        "Наименование управляющей компани": "name_of_the_management_company",
        "Наименование обслуживавшей орган": "name_of_the_service_organization",
        "Наименование источника поступлен": "source_name",
        "Оценка качества выполнения работ": "quality_evaluation",
    }
    result = {}
    for column, codename in filters.items():
        query_result_raw = await db.execute(
            sqlalchemy.text(f'select distinct "{column}" from application')
        )
        query_result = query_result_raw.scalars().all()
        result[codename] = query_result

    return result


@router.get(
    "/{application_id}",
    summary="Get one application",
)
@cache(expire=60)
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
