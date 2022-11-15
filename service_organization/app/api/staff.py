from fastapi import APIRouter, Depends, status, Response, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from typing import List
from models.staff import UserCreate, Token, User
from services.staff import StaffService, get_current_user
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(
    prefix='/staff',
    tags=['staff'],
)

@router.post('/sign-up/', response_model=Token, status_code=status.HTTP_201_CREATED)
def sign_up(
        user_data: UserCreate,
        auth_service: StaffService = Depends()
):
    """Регисртрация нового пользователя и сразу получение токена"""
    return auth_service.register_new_user(user_data)


@router.post('/sign-in/')
def sign_in(
        auth_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: StaffService = Depends()
):
    """Получение токена (токен зранится в куки)"""
    token = auth_service.authenticate_user(auth_data.username, auth_data.password)
    content = {"message": "True"}
    response = JSONResponse(content=content)
    response.set_cookie("Authorization", value=f"Bearer {token.access_token}", httponly=True)

    return response


@router.get('/user/', response_model=User)
def get_user(
        user: User = Depends(get_current_user)
):
    """Просмотр авторизованного пользователя"""
    return user


@router.get("/sign-out/")
def sign_out_and_remove_cookie(
        current_user: User = Depends(get_current_user)
):
    # Also tried following two comment lines
    # response.set_cookie(key="access_token", value="", max_age=1)
    # response.delete_cookie("access_token", domain="localhost")
    content = {"message": "Tocken closed"}
    response = JSONResponse(content=content)
    response.delete_cookie("Authorization")
    return response


@router.get("/", response_model=List[User])
def get_staff(
        service: StaffService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Запрос всех сотрудников"""
    if current_user.is_superuser:
        return service.get_all()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.get("/{name}", response_model=List[User])
def get_user(
        name: str,
        service: StaffService = Depends()
):
    """Запрос осотрудника по имени"""
    return service.get(name)


@router.post("/", response_model=User)
def create_user(
        staff_data: UserCreate,
        service: StaffService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Создание сотрудника"""
    if current_user.is_superuser:
        return service.create(data=staff_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.put('/', response_model=User)
def update_user(
        id: int,
        staff_data: UserCreate,
        service: StaffService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Обновление данных сотрудника"""
    if current_user.is_superuser:
        return service.update(id=id, data=staff_data)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(
        id: int,
        service: StaffService = Depends(),
        current_user: User = Depends(get_current_user)
):
    """Удаление сотрудника"""
    if current_user.is_superuser:
        service.delete(id=id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Только для суперюзера",
        )


@router.get("/month_birthday/", response_model=List[User])
def get_month_birthday(
        month: int,
        service: StaffService = Depends()
):
    """Запрос дней рождений за месяц"""
    return service.get_month_birthday(month=month)


@router.get("/day_birthday/", response_model=List[User])
def get_day_birthday(
        month: int,
        day: int,
        service: StaffService = Depends()
):
    """Запрос дней рождений за месяц"""
    return service.get_day_birthday(month=month, day=day)

