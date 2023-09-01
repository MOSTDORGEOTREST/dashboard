import datetime
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status, HTTPException, Query
from typing import List, Optional

from models.work import Work, WorkCreate, WorkUpdate, WorkType, WorkPrint, Report
from services.work import WorkService
from services.staff import get_current_user, User, UsersService
from services.depends import get_works_service, get_users_service

router = APIRouter(
    prefix="/works",
    tags=['works'])


@router.get("/", response_model=List[WorkPrint])
async def get_work(
        month: int = Query(qt=1, le=12),
        year: int = Query(qt=2017, le=2030),
        user_id: Optional[int] = Query(None),
        service: WorkService = Depends(get_works_service),
        current_user: User = Depends(get_current_user)
):
    """Запрос работ за текущий месяц"""
    if user_id is None:
        user_id = current_user.employee_id

    if user_id == current_user.employee_id or current_user.is_superuser:
        return await service.get_month_work(month=month, year=year, user_id=user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.post("/", response_model=WorkCreate)
async def create_work(
        data: WorkCreate,
        service: WorkService = Depends(get_works_service),
        current_user: User = Depends(get_current_user)
):
    """Создание записи в базе работ"""
    if data.employee_id == current_user.employee_id or current_user.is_superuser:
        return await service.create(data=data)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.put('/', response_model=Work)
async def update_work(
        id: int,
        data: WorkUpdate,
        service: WorkService = Depends(get_works_service),
        current_user: User = Depends(get_current_user)
):
    """Обновление записи в базе работ"""
    if data.employee_id == current_user.employee_id or current_user.is_superuser:
        return await service.update(id=id, data=data)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.delete('/', status_code=status.HTTP_200_OK)
async def delete_work(
        id: int,
        service: WorkService = Depends(get_works_service),
        current_user: User = Depends(get_current_user)
):
    """Удаление записи в базе работ"""
    work = await service.get(id)
    if work.employee_id == current_user.employee_id or current_user.is_superuser:
        await service.delete(id=id)
        content = {"message": "8====)"}
        response = JSONResponse(content=content, status_code=status.HTTP_200_OK)
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.get("/pay/{user_id}")
async def get_month_user_pay(
        month: Optional[int] = Query(None, qt=1, le=12),
        year: Optional[int] = Query(None, qt=2017, le=2030),
        user_id: Optional[int] = Query(None),
        service: WorkService = Depends(get_works_service),
        user_service: UsersService = Depends(get_users_service),
        current_user: User = Depends(get_current_user)
):
    """Расчет выплат сотрудника за месяц"""
    if user_id is None:
        user_id = current_user.employee_id

    if not month or not year:
        today = datetime.date.today()
        month = today.month
        year = today.year

    if user_id == current_user.employee_id:
        return await service.get_month_user_pay(user=current_user, month=month, year=year)
    elif current_user.is_superuser:
        user = await user_service._get(id=user_id)
        return await service.get_month_user_pay(user=user, month=month, year=year)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.get("/work-types", response_model=List[WorkType])
async def get_work_types(
        service: WorkService = Depends(get_works_service)):
    """Список работ с ценами"""
    return await service.get_work_types()


@router.get("/reports", response_model=List[Report])
async def get_reports(
        month_period: Optional[int] = Query(default=6),
        service: WorkService = Depends(get_works_service)
):
    """Запрос отчетов за все месяцы из базы"""
    return await service.get_reports(month_period=month_period)


@router.get("/report", response_model=Report)
async def get_report(
        month: Optional[int] = Query(default=None, qt=1, le=12),
        year: Optional[int] = Query(default=None, qt=2017, le=2030),
        service: WorkService = Depends(get_works_service)
):
    """Запрос отчета за конкретный месяц"""
    if not month or not year:
        current_date = datetime.date.today()
        month = current_date.month
        year = current_date.year
    return await service.get_month_reports(month=month, year=year)


@router.get("/pays")
async def get_pays(
        month_period: Optional[int] = Query(6),
        service: WorkService = Depends(get_works_service),
        current_user: User = Depends(get_current_user)
):
    """Запрос отчетов за все месяцы из базы"""
    return await service.get_pays(month_period=month_period, user=current_user)


@router.put('/check_exsistance')
async def check_exsistance(
        data: WorkUpdate,
        service: WorkService = Depends(get_works_service)
):
    """Проверка существования работы"""
    return await service.check_exsistance(data=data)

