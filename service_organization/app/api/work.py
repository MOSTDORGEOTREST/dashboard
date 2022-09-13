from fastapi import APIRouter, Depends, Response, status, HTTPException, Query
from typing import List, Optional

from models.work import Work, WorkCreate, WorkUpdate, WorkType, WorkPrint
from services.work import WorkService
from services.staff import get_current_user, User, StaffService

router = APIRouter(
    prefix="/works",
    tags=['works'])


@router.get("/", response_model=List[WorkPrint])
def get_work(
        month: int,
        year: int,
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


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_work(
        id: int,
        service: WorkService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Удаление записи в базе работ"""
    work = service.get(id)
    if work.user_id == current_user.id or current_user.is_superuser:
        service.delete(id=id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.get("/pay/")
def get_month_user_pay(
        month: int,
        year: int,
        user_id: Optional[int] = Query(None),
        service: WorkService = Depends(),
        user_service: StaffService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Расчет выплат сотрудника за месяц"""
    if user_id is None:
        user_id = current_user.id

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




