from fastapi import APIRouter, Depends, Response, status
from typing import List
from datetime import date

from models.prize import Prize
from services.depends import get_prizes_service
from services.prize import PrizesService

router = APIRouter(
    prefix="/prizes",
    tags=['prizes'])


@router.get("/", response_model=List[Prize])
async def get_prizes(service: PrizesService = Depends(get_prizes_service)):
    """Запрос премий за все месяцы из базы"""
    return await service.get_all()


@router.get("/{date}", response_model=Prize)
async def get_prize(date: date = None, service: PrizesService = Depends(get_prizes_service)):
    """Запрос премии за конкретный месяц. Всегда 25 число"""
    return await service.get(date)


@router.post("/", response_model=Prize)
async def create_prize(prize_data: Prize, service: PrizesService = Depends(get_prizes_service)):
    """Создание записи в базе премии. Если запись существует, то будет автоматическое обновление. Всегда 25 число"""
    return await service.create(prize_data=prize_data)


@router.put('/', response_model=Prize)
async def update_prize(date: date, prize_data: Prize, service: PrizesService = Depends(get_prizes_service)):
    """Обновление записи в базе премии. Всегда 25 число"""
    return await service.update(date=date, prize_data=prize_data)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_prize(date: date, service: PrizesService = Depends(get_prizes_service)):
    """Удаление записи в базе премии. Всегда 25 число"""
    await service.delete(date=date)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


