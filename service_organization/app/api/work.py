import datetime
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, Response, status, HTTPException, Query
from typing import List, Optional
from datetime import date

from models.work import Work, WorkCreate, WorkUpdate, WorkType, WorkPrint, Report
from services.work import WorkService
from services.staff import get_current_user, User, StaffService

router = APIRouter(
    prefix="/works",
    tags=['works'])


@router.get("/", response_model=List[WorkPrint])
def get_work(
        month: int = Query(qt=1, le=12),
        year: int = Query(qt=2017, le=2030),
        user_id: Optional[int] = Query(None),
        service: WorkService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Запрос работ за текущий месяц"""
    if user_id is None:
        user_id = current_user.id

    if user_id == current_user.id or current_user.is_superuser:
        return service.get_month_work(month=month, year=year, user_id=user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.post("/", response_model=WorkCreate)
def create_work(
        data: WorkCreate,
        service: WorkService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Создание записи в базе работ"""
    if data.user_id == current_user.id or current_user.is_superuser:
        return service.create(data=data)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.put('/', response_model=Work)
def update_work(
        id: int,
        data: WorkUpdate,
        service: WorkService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Обновление записи в базе работ"""
    if data.user_id == current_user.id or current_user.is_superuser:
        return service.update(id=id, data=data)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.delete('/', status_code=status.HTTP_200_OK)
def delete_work(
        id: int,
        service: WorkService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Удаление записи в базе работ"""
    work = service.get(id)
    if work.user_id == current_user.id or current_user.is_superuser:
        service.delete(id=id)
        content = {"message": "8====)"}
        response = JSONResponse(content=content, status_code=status.HTTP_200_OK)
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.get("/pay/{user_id}")
def get_month_user_pay(
        month: Optional[int] = Query(None, qt=1, le=12),
        year: Optional[int] = Query(None, qt=2017, le=2030),
        user_id: Optional[int] = Query(None),
        service: WorkService = Depends(),
        user_service: StaffService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Расчет выплат сотрудника за месяц"""
    if user_id is None:
        user_id = current_user.id

    if not month or not year:
        today = datetime.date.today()
        month = today.month
        year = today.year

    if user_id == current_user.id:
        return service.get_month_user_pay(user=current_user, month=month, year=year)
    elif current_user.is_superuser:
        user = user_service._get(id=user_id)
        return service.get_month_user_pay(user=user, month=month, year=year)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.get("/work-types", response_model=List[WorkType])
def get_work_types(
        service: WorkService = Depends()):
    """Список работ с ценами"""
    return service.get_work_types()


@router.get("/reports", response_model=List[Report])
def get_reports(
        month_period: Optional[int] = Query(default=6),
        service: WorkService = Depends()
):
    """Запрос отчетов за все месяцы из базы"""
    return service.get_reports(month_period=month_period)


@router.get("/report", response_model=Report)
def get_report(
        month: Optional[int] = Query(default=None, qt=1, le=12),
        year: Optional[int] = Query(default=None, qt=2017, le=2030),
        service: WorkService = Depends()
):
    """Запрос отчета за конкретный месяц"""
    if not month or not year:
        current_date = datetime.date.today()
        month = current_date.month
        year = current_date.year
    return service.get_month_reports(month=month, year=year)


@router.get("/pays")
def get_pays(
        month_period: Optional[int] = Query(6),
        service: WorkService = Depends()
):
    """Запрос отчетов за все месяцы из базы"""
    return service.get_pays(month_period=month_period)


@router.get("/pay")
def get_pay(
        month: Optional[int] = Query(default=None, qt=1, le=12),
        year: Optional[int] = Query(default=None, qt=2017, le=2030),
        service: WorkService = Depends()
):
    """Запрос отчета за конкретный месяц"""
    if not month or not year:
        current_date = datetime.date.today()
        month = current_date.month
        year = current_date.year
    return service.get_month_pay(month=month, year=year)


@router.put('/check_exsistance')
def check_exsistance(
        data: WorkUpdate,
        service: WorkService = Depends()
):
    """Проверка существования работы"""
    return service.check_exsistance(data=data)

