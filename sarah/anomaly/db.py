import itertools as it 
import typing as tp

import fastapi
import sqlalchemy
from sqlalchemy.ext import asyncio as aorm

from sarah import deps


# internal

def _make_group_by(
    list: tp.List[tp.Dict],
    key: str
) -> tp.Dict[str, dict]:
    output: dict = {}
    
    for d in list:
        output[d[key]] = d
    
    return output


async def get_anomaly_criteria(
    db: aorm.AsyncSession,
    log: tp.Any,
    groupby_key: str = "Наименование"
) -> tp.Dict[str, dict]:
    query = await db.execute(
        sqlalchemy.text(
            """
            SELECT
                *
            FROM anomaly_criteria;
            """
        )
    )
    return _make_group_by(query.mappings().all(), key=groupby_key)


async def get_short_defects_ids(
    db: aorm.AsyncSession,
    log: tp.Any
) -> tp.List[str]:
    query = await db.execute(
        sqlalchemy.text(
            """
            SELECT
                "Идентификатор"
            FROM short_defects;
            """
        )
    )
    return list(query.scalars())


async def get_restricted_repeated_applications(
    db: aorm.AsyncSession,
    log: tp.Any
) -> tp.List[str]:
    query = await db.execute(
        sqlalchemy.text(
            """
            SELECT
                "Идентификатор"
            FROM restricted_repeated_applications;
            """
        )
    )
    return list(query.scalars())


async def get_close_wo_completion_first(
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    batch_size: int = 100
) -> tp.List[dict]:
    query = await db.stream(
        sqlalchemy.text(
            """
            SELECT
                id,
                "Дата закрытия",
                "Наименование дефекта",
                applicant_id,
                application.application_creation_timestamp as application_creation_timestamp
            FROM application
            WHERE "Наименование статуса заявки" IN ('Закрыта', 'Закрыта через МАРМ')
                AND "Наименование дефекта" NOT IN ('Ввод в эксплуатацию ИПУ воды (замена, демонтаж, пропуск межповерочного интервала)', 'Подача документов о поверке ИПУ
            воды в электронном виде')
                AND "Результативность" != 'Выполнено'
                AND "Вид выполненных работ" != 'Аварийное/плановое отключение' 
                AND is_anomaly = false
            LIMIT 1000;
            """
        ),
        execution_options={"yield_per": batch_size, "stream_results": True}
    )

    data = await query.mappings().fetchmany(batch_size)
    while data:
        yield(data)
        data = await query.mappings().fetchmany(batch_size)


async def get_close_wo_completion_second(
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    batch_size: int = 100
) -> tp.List[dict]:
    query = await db.stream(
        sqlalchemy.text(
            """
            SELECT
                id,
                "Дата закрытия",
                "Наименование дефекта",
                applicant_id,
                application.application_creation_timestamp as application_creation_timestamp
            FROM application
            WHERE "Наименование статуса заявки" IN ('Закрыта', 'Закрыта через МАРМ')
                AND "Наименование дефекта" NOT IN ('Ввод в эксплуатацию ИПУ воды (замена, демонтаж, пропуск межповерочного интервала)', 'Подача документов о поверке ИПУ
            воды в электронном виде')
                AND "Результативность" = 'Выполнено'
                AND COALESCE(EXTRACT(epoch FROM application.application_closure_timestamp - application.application_creation_timestamp), 0) / 60 > 10
                AND ("Кол-во возвратов на доработку" IS NULL OR "Кол-во возвратов на доработку" = '0') 
                AND is_anomaly = false
            LIMIT 1000
            """
        ),
        execution_options={"yield_per": batch_size, "stream_results": True}
    )

    data = await query.mappings().fetchmany(batch_size)
    while data:
        yield(data)
        data = await query.mappings().fetchmany(batch_size)


async def get_close_wo_completion_third(
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    batch_size: int = 100
) -> tp.List[dict]:
    query = await db.stream(
        sqlalchemy.text(
            """
            SELECT
                id,
                "Дата закрытия",
                "Наименование дефекта",
                "Идентификатор дефекта",
                applicant_id,
                application.application_creation_timestamp as application_creation_timestamp
            FROM application
            WHERE "Наименование статуса заявки" IN ('Закрыта', 'Закрыта через МАРМ')
                AND "Результативность" = 'Выполнено'
                AND ("Кол-во возвратов на доработку" IS NULL OR "Кол-во возвратов на доработку" = '0')
                AND COALESCE(EXTRACT(epoch FROM application.application_closure_timestamp - application.application_creation_timestamp), 0) / 60 < 10
                AND is_anomaly = false
            LIMIT 1000;
            """
        ),
        execution_options={"yield_per": batch_size, "stream_results": True}
    )

    data = await query.mappings().fetchmany(batch_size)
    while data:
        yield(data)
        data = await query.mappings().fetchmany(batch_size)


async def get_close_wo_completion_fourth(
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    batch_size: int = 100
) -> tp.List[dict]:
    query = await db.stream(
        sqlalchemy.text(
            """
            SELECT
                id,
                "Дата закрытия",
                "Наименование дефекта",
                "Идентификатор дефекта",
                applicant_id,
                application.application_creation_timestamp as application_creation_timestamp
            FROM application
            WHERE "Наименование статуса заявки" IN ('Закрыта', 'Закрыта через МАРМ')
                AND "Результативность" = 'Выполнено'
                AND "Кол-во возвратов на доработку" IS NOT NULL AND "Кол-во возвратов на доработку" != '0'
                AND COALESCE(EXTRACT(epoch FROM application.application_closure_timestamp - application.application_creation_timestamp), 0) / 60 < 10
                AND is_anomaly = false
            LIMIT 1000;
            """
        ),
        execution_options={"yield_per": batch_size, "stream_results": True}
    )

    data = await query.mappings().fetchmany(batch_size)
    while data:
        yield(data)
        data = await query.mappings().fetchmany(batch_size)


async def get_close_wo_completion_fifth(
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger),
    batch_size: int = 100
) -> tp.List[dict]:
    query = await db.stream(
        sqlalchemy.text(
            """
            SELECT
                id,
                "Дата закрытия",
                "Наименование дефекта",
                "Идентификатор дефекта",
                applicant_id,
                application.application_creation_timestamp as application_creation_timestamp
            FROM application
            WHERE "Наименование статуса заявки" IN ('Закрыта', 'Закрыта через МАРМ')
                AND "Результативность" = 'Выполнено'
                AND "Кол-во возвратов на доработку" IS NOT NULL AND "Кол-во возвратов на доработку" != '0'
                AND is_anomaly = false
            LIMIT 1000;
            """
        ),
        execution_options={"yield_per": batch_size, "stream_results": True}
    )

    data = await query.mappings().fetchmany(batch_size)
    while data:
        yield(data)
        data = await query.mappings().fetchmany(batch_size)


async def update_applications_is_anomaly(
    ids: list,
    db: aorm.AsyncSession = fastapi.Depends(deps.get_async_db),
    log: tp.Any = fastapi.Depends(deps.logger)
):
    query = await db.execute(
        sqlalchemy.text(
            """
            UPDATE application
            SET is_anomaly = True
            WHERE id IN (:ids);
            """
        ).bindparams(ids=ids)
    )
    return query
