import math
import typing
from datetime import datetime

import fastapi
import sqlalchemy
import sqlalchemy as sa
from fastapi_cache.decorator import cache
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


def make_v2_list(res):
    res_v2 = []
    for one_res in res:
        i = 0
        one_res_v2 = {}
        for key, value in one_res.items():
            if key == "geo_coordinates":
                one_res_v2["geo_coordinates"] = value
            one_res_v2[str(i)] = value
            i += 1
        res_v2.append(one_res_v2)
    return res_v2


def make_v2_one(res):
    i = 0
    one_res_v2 = {}
    for key, value in res.items():
        if key == "geo_coordinates":
            one_res_v2["geo_coordinates"] = value
        one_res_v2[str(i)] = value
        i += 1
    return one_res_v2


@router.get(
    "/",
)
@cache(expire=300)
async def get_applications(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
    multi: deps.Multi = fastapi.Depends(),
    is_anomaly: bool | None = fastapi.Query(default=None),
    # ???????????????????????? ?????????????????? ??????????????
    defect_category_name: typing.List[str] | None = fastapi.Query(default=None),
    # ?????? ?????????????????????? ??????????
    type_of_work_performed: typing.List[str] | None = fastapi.Query(default=None),
    # ?????? ????????????
    district_code: typing.List[str] | None = fastapi.Query(default=None),
    # ???????????????????????? ????????????
    district_name: list[str] | None = fastapi.Query(default=None),
    # ???????????????????????? ?????????????????????? ??????????????
    name_of_the_management_company: list[str] | None = fastapi.Query(default=None),
    # ???????????????????????? ?????????????????????????? ??????????
    name_of_the_service_organization: list[str] | None = fastapi.Query(default=None),
    # ???????????????????????? ?????????????????? ??????????????????
    source_name: list[str] | None = fastapi.Query(default=None),
    # ???????????? ???????????????? ???????????????????? ??????????
    quality_evaluation: list[str] | None = fastapi.Query(default=None),
    creation_timestamp_start: datetime | None = fastapi.Query(default=None),
    creation_timestamp_end: datetime | None = fastapi.Query(default=None),
    query: str | None = fastapi.Query(default=None),
    with_comment: bool | None = fastapi.Query(default=None),
    result_desc: list[str] | None = fastapi.Query(default=None),
    urgency: list[str] | None = fastapi.Query(default=None),
) -> typing.Any:
    filters = {
        "???????????????????????? ?????????????????? ??????????????": defect_category_name,
        "?????? ?????????????????????? ??????????": type_of_work_performed,
        "?????? ????????????": district_code,
        "???????????????????????? ????????????": district_name,
        "???????????????????????? ?????????????????????? ??????????????": name_of_the_management_company,
        "???????????????????????? ?????????????????????????? ??????????": name_of_the_service_organization,
        "???????????????????????? ?????????????????? ??????????????????": source_name,
        "???????????? ???????????????? ???????????????????? ??????????": quality_evaluation,
        "????????????????????????????????": result_desc,
        "???????????????????????? ?????????????????? ??????????????????:": urgency,
    }
    time_filters = [
        ("timestamp_start", creation_timestamp_start, ">"),
        ("timestamp_start", creation_timestamp_end, "<"),
    ]
    statement = sa.select(sa.text("* from application"))
    statement = apply_where_filters(statement, filters)
    statement = apply_time_filters(statement, time_filters, "application")

    if is_anomaly is not None:
        statement = statement.where(sa.Column("is_anomaly").__eq__(is_anomaly))

    if query is not None and len(query) > 0:
        statement = statement.where(
            sa.text("compound LIKE '%' || :query_param || '%'").bindparams(
                sa.bindparam(
                    "query_param",
                    value=query,
                )
            )
        )

    if with_comment is not None:
        column = sqlalchemy.Column("??????????????????????")
        if with_comment:
            statement = statement.where(column.isnot(None))
        else:
            statement = statement.where(column.is_(None))

    statement_paged = (
        statement.order_by(sa.Column("id")).limit(multi.limit).offset(multi.offset)
    )
    res_raw_cor = db.execute(statement_paged)
    res_raw = await res_raw_cor
    res = res_raw.mappings().all()
    if len(res) < multi.limit:
        return {"res": make_v2_list(res), "count_pages": 1}

    estimate_statement = statement.compile(
        dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
    )
    res_count_raw = await db.execute(
        sqlalchemy.text(f"select row_estimator($${estimate_statement}$$);")
    )
    res_count = res_count_raw.scalar_one()
    count_pages = math.ceil(res_count / multi.limit)
    return {"res": make_v2_list(res), "count_pages": count_pages}


@router.get(
    "/anomalies",
)
@cache(expire=300)
async def anomalies(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
) -> typing.Any:
    query = await db.execute(
        sqlalchemy.text(
            'select id, geo_coordinates, "???????????????????????? ??????????????" from application where geo_coordinates is not NULL and is_anomaly = true'
        )
    )
    applications = query.mappings().all()
    if applications is None or len(applications) == 0:
        raise fastapi.HTTPException(
            404, "Either no anomalies found or they haven't been geotagged yet."
        )
    return make_v2_list(applications)


@router.get(
    "/meta",
    summary="Get metadata",
)
@cache(expire=1200)
async def meta(
    *,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: typing.Any = fastapi.Depends(deps.logger),
) -> typing.Any:
    filters = {
        "???????????????????????? ?????????????????? ??????????????": "defect_category_name",
        "?????? ?????????????????????? ??????????": "type_of_work_performed",
        "?????? ????????????": "district_code",
        "???????????????????????? ????????????": "district_name",
        "???????????????????????? ?????????????????????? ??????????????": "name_of_the_management_company",
        "???????????????????????? ?????????????????????????? ??????????": "name_of_the_service_organization",
        "???????????????????????? ?????????????????? ??????????????????": "source_name",
        "???????????? ???????????????? ???????????????????? ??????????": "quality_evaluation",
        "????????????????????????????????": "result_desc",
        "???????????????????????? ?????????????????? ??????????????????:": "urgency",
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
@cache(expire=300)
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
    return make_v2_one(application[0])
