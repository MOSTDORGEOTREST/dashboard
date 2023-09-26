import datetime
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, Response, status, HTTPException, Query
from typing import List, Optional
from datetime import date

from models.reports import Report, ReportUpdate, ReportCreate
from services.reports import ReportService

router = APIRouter(
    prefix="/reports",
    tags=['reports'])


@router.get("/{object_number}")
def get_object(
        object_number: str,
        service: ReportService = Depends(),
):
    """Получение всех протоколов в объекте"""
    return service.get_object(object_number=object_number)


@router.get("/control/{object_number}")
def get_object_control(
        object_number: str,
        service: ReportService = Depends(),
):
    """Получение всех протоколов в объекте"""
    res = {}
    data = service.get_object(object_number=object_number)
    for i in data:
        if res.get(i.test_type, None):
            res[i.test_type] += 1
        else:
            res[i.test_type] = 1
    return res


@router.get("/objects/")
def get_objects(
        service: ReportService = Depends(),
):
    """Полкчение всех объектов"""
    return service.get_objects()


@router.post("/", response_model=ReportCreate)
def create_report(
        data: ReportCreate,
        service: ReportService = Depends(),
):
    """Создание записи в базе"""
    return service.create(data=data)


@router.put('/', response_model=Report)
def update_report(
        id: int,
        data: ReportUpdate,
        service: ReportService = Depends(),
):
    """Обновление записи в базе"""
    return service.update(id=id, data=data)


@router.delete('/', status_code=status.HTTP_200_OK)
def delete_report(
        id: int,
        service: ReportService = Depends(),
):
    """Удаление записи в базе работ"""
    service.delete(id=id)
    content = {"message": "8====)"}
    response = JSONResponse(content=content, status_code=status.HTTP_200_OK)
    return response


