import itertools as it 
import typing as tp

import fastapi
import sqlalchemy
from sqlalchemy.ext import asyncio as aorm
from sqlalchemy import orm

from sarah import deps
from sarah.anomaly import db as db_queries


"""
статус = Наименование статуса заявки
тип дефекта = Наименование дефекта
результативность = Результативность
результат закрытия = Вид выполненных работ
id заявителя = "Адрес проблемы" + "Подъезд" + "Этаж" + "Квартира" = applicant_id
Корневой идентификатор (прил 3) = Корневой идентификатор категории дефекта (application) = Корневой идентификат (anomaly_criteria)
время закрытия = "Дата закрытия"
"""


# internal


async def _get_anomaly_applications(
    applications: tp.Dict[str, tp.List[dict]],
    anomaly_criteria: tp.Dict[str, dict],
    log: tp.Any
) -> tp.List[dict]:
    anomaly_applications: tp.List[dict] = []

    # filter for anomaly applications
    anomaly_applications_with_duplicates: tp.List[dict] = []
    for applicant_id_name_of_defect, applications_group in applications.items():
        name_of_defect = applicant_id_name_of_defect.split("_")[1]
        if name_of_defect not in anomaly_criteria:
            continue
        max_time = int(anomaly_criteria[name_of_defect]["Повторное срок, часов"]) if anomaly_criteria[name_of_defect]["Повторное срок, часов"] != "-" else 10**9
        for i in range(len(applications_group) - 1):
            if (applications_group[i + 1]["application_creation_timestamp"] - applications_group[i]["application_creation_timestamp"]).seconds < max_time*3600:
                anomaly_applications_with_duplicates.extend(applications_group[i:i + 1])
    
    # delete duplicated applications by id
    ids = []
    for application in anomaly_applications_with_duplicates:
        if application["id"] not in ids:
            anomaly_applications.append(application)
    return anomaly_applications


async def get_close_wo_completion_first(
    *,
    db: aorm.AsyncSession,
    log: tp.Any,
) -> tp.List[dict]:
    # group applications to dict with applicant_id_name_of_defect
    applications: tp.Dict[str, tp.List[dict]] = {}
    async for yield_applications in db_queries.get_close_wo_completion_first(db=db, log=log):
        sorted_applications = sorted(yield_applications, key=lambda item: item.get("Дата закрытия"))
        for key, group in it.groupby(sorted_applications, key=lambda item: str(item["applicant_id"]) + "_" + str(item["Наименование дефекта"])):
            for item in group:
                if key in applications:
                    applications[key].append(item)
                else:
                    applications[key] = [item]
    
    anomaly_criteria = await db_queries.get_anomaly_criteria(db=db, log=log)

    anomaly_applications = await _get_anomaly_applications(applications, anomaly_criteria, log)
    
    return anomaly_applications


async def get_close_wo_completion_second(
    *,
    db: aorm.AsyncSession,
    log: tp.Any,
) -> tp.List[dict]:
    # group applications to dict with applicant_id_name_of_defect
    applications: tp.Dict[str, tp.List[dict]] = {}
    async for yield_applications in db_queries.get_close_wo_completion_second(db=db, log=log):
        sorted_applications = sorted(yield_applications, key=lambda item: item.get("Дата закрытия"))
        for key, group in it.groupby(sorted_applications, key=lambda item: str(item["applicant_id"]) + "_" + str(item["Наименование дефекта"])):
            for item in group:
                if key in applications:
                    applications[key].append(item)
                else:
                    applications[key] = [item]
    
    anomaly_criteria = await db_queries.get_anomaly_criteria(db=db, log=log)

    anomaly_applications = await _get_anomaly_applications(applications, anomaly_criteria, log)

    return anomaly_applications


async def get_close_wo_completion_third(
    *,
    db: aorm.AsyncSession,
    log: tp.Any,
) -> tp.List[dict]:    
    short_defects_ids = await db_queries.get_short_defects_ids(db=db, log=log)

    # group applications to dict with applicant_id_name_of_defect
    applications: tp.Dict[str, tp.List[dict]] = {}
    async for yield_applications in db_queries.get_close_wo_completion_third(db=db, log=log):
        sorted_applications = sorted(yield_applications, key=lambda item: item.get("Дата закрытия"))
        for key, group in it.groupby(sorted_applications, key=lambda item: str(item["applicant_id"]) + "_" + str(item["Наименование дефекта"])):
            for item in group:
                if item["Идентификатор дефекта"] not in short_defects_ids:
                    continue
                if key in applications:
                    applications[key].append(item)
                else:
                    applications[key] = [item]
    
    anomaly_criteria = await db_queries.get_anomaly_criteria(db=db, log=log)

    anomaly_applications = await _get_anomaly_applications(applications, anomaly_criteria, log)
    
    return anomaly_applications
    

async def get_close_wo_completion_fourth(
    *,
    db: aorm.AsyncSession,
    log: tp.Any,
) -> tp.List[dict]:    
    short_defects_ids = await db_queries.get_short_defects_ids(db=db, log=log)

    # group applications to dict with applicant_id_name_of_defect
    applications: tp.Dict[str, tp.List[dict]] = {}
    async for yield_applications in db_queries.get_close_wo_completion_fourth(db=db, log=log):
        sorted_applications = sorted(yield_applications, key=lambda item: item.get("Дата закрытия"))
        for key, group in it.groupby(sorted_applications, key=lambda item: str(item["applicant_id"]) + "_" + str(item["Наименование дефекта"])):
            for item in group:
                if item["Идентификатор дефекта"] in short_defects_ids:
                    continue
                if key in applications:
                    applications[key].append(item)
                else:
                    applications[key] = [item]
    
    anomaly_criteria = await db_queries.get_anomaly_criteria(db=db, log=log)

    anomaly_applications = await _get_anomaly_applications(applications, anomaly_criteria, log)
    
    return anomaly_applications


async def get_close_wo_completion_fifth(
    *,
    db: aorm.AsyncSession,
    log: tp.Any,
) -> tp.List[dict]:    
    restricted_repeated_applications_ids = await db_queries.get_restricted_repeated_applications(db=db, log=log)

    # group applications to dict with applicant_id_name_of_defect
    applications: tp.Dict[str, tp.List[dict]] = {}
    async for yield_applications in db_queries.get_close_wo_completion_fifth(db=db, log=log):
        sorted_applications = sorted(yield_applications, key=lambda item: item.get("Дата закрытия"))
        for key, group in it.groupby(sorted_applications, key=lambda item: str(item["applicant_id"]) + "_" + str(item["Наименование дефекта"])):
            for item in group:
                if item["Идентификатор дефекта"] not in restricted_repeated_applications_ids:
                    continue
                if key in applications:
                    applications[key].append(item)
                else:
                    applications[key] = [item]
    
    anomaly_criteria = await db_queries.get_anomaly_criteria(db=db, log=log)

    anomaly_applications = await _get_anomaly_applications(applications, anomaly_criteria, log)
    
    return anomaly_applications
