from passlib.hash import bcrypt
from datetime import datetime, timedelta, date
from pydantic import ValidationError
from sqlalchemy.future import select
from sqlalchemy import update, delete, literal
from jose import jwt, JWTError
from typing import List
from typing import Optional, Dict
from fastapi import Depends, Request, status, HTTPException
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.sql import extract
from sqlalchemy.orm import Session
from sqlalchemy import func

from config import configs
from db import tables
from models.staff import User, Token, UserCreate, UserUpdate, LowUser

__hash__ = lambda obj: id(obj)

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Token]:
        authorization_headers = request.headers.get("Authorization")
        authorization_cookies = request.cookies.get("Authorization")

        authorization = authorization_cookies if authorization_cookies else authorization_headers

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise exception_token

        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl='/authorization/sign-in/')


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return UsersService.verify_token(token)


class UsersService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> User:
        try:
            payload = jwt.decode(
                token,
                configs.jwt_secret,
                algorithms=[configs.jwt_algorithm],
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is wrong or missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_data = payload.get('user')

        print(user_data)

        user_data['birthday'] = datetime.strptime(user_data['birthday'], "%d.%m.%Y").date()

        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is wrong or missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    @classmethod
    def create_token(cls, user: tables.staff, exp=None) -> Token:
        user_data = User.from_orm(user)
        user_data = user_data.dict()
        user_data['birthday'] = user_data['birthday'].strftime("%d.%m.%Y")
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(hours=configs.jwt_expiration) if not exp else exp,
            'sub': str(user_data['employee_id']),
            'user': user_data,
        }
        token = jwt.encode(
            payload,
            configs.jwt_secret,
            algorithm=configs.jwt_algorithm,
        )
        return Token(access_token=token)

    def __init__(self, session: Session):
        self.session = session

    async def get(self, id: int) -> tables.staff:
        users = await self.session.execute(
            select(tables.staff).
            filter_by(id=id)
        )
        user = users.scalars().first()
        return user

    async def find(self, string: int) -> List[tables.staff]:
        users = await self.session.execute(
            select(tables.staff).
            where(
                func.position(
                    literal(string.lower()).op('IN')(
                        func.lower(
                            func.concat(
                                tables.staff.last_name,
                                tables.staff.first_name
                            )
                        )
                    )
                ) != 0
            )
        )
        users = users.scalars().all()

        return [
            LowUser(
                first_name=user.first_name,
                middle_name=user.middle_name,
                last_name=user.last_name,
                phone_number=user.phone_number,
                birthday=user.birthday,
            ) for user in users
        ]

    async def register_new_user(self, user_data: UserCreate) -> Token:
        phones = await self.session.execute(
            select(tables.staff).
            filter_by(phone=user_data.phone_number)
        )

        phones = phones.scalars().first()

        if phones:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This phone is already exist",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = tables.staff(
            first_name=user_data.first_name,
            middle_name=user_data.middle_name,
            last_name=user_data.last_name,
            password_hash=self.hash_password(user_data.password),
            phone_number=user_data.phone_number,
            birthday=user_data.birthday,
            is_superuser=user_data.is_superuser,
            rate=user_data.rate,
            developer_percent=user_data.developer_percent,
        )

        self.session.add(user)
        await self.session.commit()
        return user

    async def authenticate_user(self, user_id: int, password: str) -> Token:
        user = await self.session.execute(
            select(tables.staff).
            filter(tables.staff.employee_id == user_id)
        )

        user = user.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect user_id or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        if not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect user_id or password xdhxdfhxdfh',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return self.create_token(user)

    async def get_token(self, user_id) -> Token:
        user = await self.session.execute(
            select(tables.staff)
            .filter(tables.staff.employee_id == user_id)
        )

        user = user.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect user_id or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return self.create_token(user)

    async def get_all(self) -> List[tables.staff]:
        users = await self.session.execute(
            select(tables.staff)
        )
        users = users.scalars().all()
        return users

    async def get_month_birthday(self, month: int) -> List[tables.staff]:
        users = await self.session.execute(
            select(tables.staff).
            filter(extract('month', tables.staff.birthday) == month).
            order_by(extract('day', tables.staff.birthday))
        )
        return users.scalars().all()

    async def get_day_birthday(self, month: int, day: int) -> List[tables.staff]:
        users = await self.session.execute(
            select(tables.staff).
            filter(extract('month', tables.staff.birthday) == month).
            filter(extract('day', tables.staff.birthday) == day).
            order_by(tables.staff.last_name)
        )
        return users.scalars().all()

    async def update(self, id: int, user_data: UserUpdate) -> tables.staff:
        q = update(tables.staff).where(tables.staff.employee_id == id).values(
            user_data.to_dict()
        )

        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()
        return user_data

    async def delete(self, id: int):
        q = delete(tables.staff).where(tables.staff.employee_id == id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)

