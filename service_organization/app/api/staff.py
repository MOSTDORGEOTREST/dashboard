from fastapi import APIRouter, Depends, status, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import List

from models.staff import UserCreate, Token, User, UserUpdate, LowUser
from services.staff import UsersService, get_current_user
from services.depends import get_users_service

router = APIRouter(
    prefix='/staff',
    tags=['staff'],
)

@router.get('/', response_model=List[User])
async def get_all(
        auth_service: UsersService = Depends(get_users_service)
):
    """Просмотр всех пользователей"""
    return await auth_service.get_all()

@router.post('/', response_model=User)
async def sign_up(
        user_data: UserCreate,
        auth_service: UsersService = Depends(get_users_service),
        current_user: User = Depends(get_current_user)
):
    """Регисртрация нового пользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have the right to do this",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.register_new_user(user_data)

@router.post('/sign-in/')
async def sign_in(
        auth_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: UsersService = Depends(get_users_service)
):
    """Получение токена (токен зранится в куки)"""
    token = await auth_service.authenticate_user(int(auth_data.username), auth_data.password)
    content = {"message": "True"}
    response = JSONResponse(content=content)
    response.set_cookie("Authorization", value=f"Bearer {token.access_token}", httponly=True)
    return response

@router.post('/token/', response_model=Token)
async def get_token(
        user: User = Depends(get_current_user),
        auth_service: UsersService = Depends(get_users_service)
):
    """Получение токена"""
    return await auth_service.get_token(user.id)

@router.get('/user/', response_model=User)
async def get_user(
        user: User = Depends(get_current_user)
):
    """Просмотр авторизованного пользователя"""
    return user

@router.get("/sign-out/")
async def sign_out_and_remove_cookie(
        current_user: User = Depends(get_current_user)
):
    content = {"message": "Tocken closed"}
    response = JSONResponse(content=content)
    response.delete_cookie("Authorization")
    return response

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        id: int,
        auth_service: UsersService = Depends(get_users_service),
        current_user: User = Depends(get_current_user)
):
    """Удаление пользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have the right to do this",
            headers={"WWW-Authenticate": "Bearer"},
        )
    await auth_service.delete(id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put('/')
async def update_user(
        id: int, user_data: UserUpdate,
        auth_service: UsersService = Depends(get_users_service),
        current_user: User = Depends(get_current_user)
):
    """Обновление данных пользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Don't have the right to do this",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.update(id=id, user_data=user_data)

@router.get("/month_birthday/", response_model=List[User])
async def get_month_birthday(
        month: int,
        service: UsersService = Depends(get_users_service)
):
    """Запрос дней рождений за месяц"""
    return await service.get_month_birthday(month=month)


@router.get("/day_birthday/", response_model=List[User])
async def get_day_birthday(
        month: int,
        day: int,
        service: UsersService = Depends(get_users_service)
):
    """Запрос дней рождений за месяц"""
    return await service.get_day_birthday(month=month, day=day)


@router.get("/{string}", response_model=List[LowUser])
async def find_user(
        string: str,
        service: UsersService = Depends(get_users_service)
):
    """Запрос осотрудника по имени"""
    return await service.find(string)