from typing import List
from sqlalchemy.sql import extract
from passlib.hash import bcrypt
from datetime import datetime, timedelta, date
from pydantic import ValidationError
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
from typing import Optional, Dict
from fastapi import status, HTTPException, Depends, Request
from jose import jwt, JWTError

from db import tables
from models.staff import User, Token, UserCreate, UserUpdate
from settings import settings
from db.database import get_session

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
        authorization: str = request.cookies.get("Authorization")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is wrong or missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl='/staff/sign-in/')


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return StaffService.verify_token(token)


class StaffService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'Authenticate': 'Bearer'},
        )

        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
        except JWTError:
            raise exception from None

        user_data = payload.get('user')
        day, month, year = user_data["birthday"].split(".")
        user_data["birthday"] = date(year=int(year), month=int(month), day=int(day))

        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise exception from None

        return user

    @classmethod
    def create_token(cls, user: tables.Staff) -> Token:
        user_data = User.from_orm(user)
        now = datetime.utcnow()
        user_data.dict()
        user_data = user_data.dict()
        user_data["birthday"] = f"{user_data['birthday'].day}.{user_data['birthday'].month}.{user_data['birthday'].year}"

        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(days=settings.jwt_expiration),
            'sub': str(user_data["id"]),
            'user': user_data,
        }
        token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
        return Token(access_token=token)

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def register_new_user(self, user_data: UserCreate) -> Token:
        user_names = (
            self.session
                .query(tables.Staff)
                .filter(tables.Staff.full_name == user_data.full_name)
                .first()
        )

        if user_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEND,
                detail="This name is already exist",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = tables.Staff(
            full_name=user_data.full_name,
            password_hash=self.hash_password(user_data.password),
            phone_number=user_data.phone_number,
            birthday=user_data.birthday,
            is_superuser=user_data.is_superuser,
            rate=user_data.rate,
        )

        self.session.add(user)
        self.session.commit()
        return self.create_token(user)

    def authenticate_user(self, username: str, password: str) -> Token:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        user = (
            self.session
            .query(tables.Staff)
            .filter(tables.Staff.full_name == username)
            .first()
        )

        if not user:
            raise exception

        if not self.verify_password(password, user.password_hash):
            raise exception

        return self.create_token(user)

    def _get(self, id: int) -> Optional[tables.Staff]:
        employee = self.session.query(tables.Staff).filter_by(id=id).first()

        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return employee

    def get_all(self) -> List[tables.Staff]:
        return self.session.query(tables.Staff).order_by(tables.Staff.full_name).all()

    def get_month_birthday(self, month) -> List[tables.Staff]:
        return self.session.query(tables.Staff).filter(extract('month', tables.Staff.birthday) == month).order_by(extract('day', tables.Staff.birthday)).all()

    def get_day_birthday(self, month, day) -> List[tables.Staff]:
        return self.session.query(tables.Staff).filter(extract('month', tables.Staff.birthday) == month).filter(extract('day', tables.Staff.birthday) == day).order_by(tables.Staff.full_name).all()

    def get(self, name: str) -> Optional[tables.Staff]:
        staff = self.session.query(tables.Staff).all()

        if not staff:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        res = []

        for employee in staff:
            if name.upper() in str(employee.full_name).upper():
                res.append(employee)

        return res

    def create(self, data: UserCreate) -> tables.Staff:
        data = data.dict()
        data["password_hash"] = bcrypt.hash(data["password"])
        data.pop("password")
        staff = tables.Staff(
            **data)
        self.session.add(staff)
        self.session.commit()
        return staff

    def update(self, id: int, data: UserUpdate) -> tables.Staff:
        employee = self._get(id)
        for field, value in data:
            setattr(employee, field, value)
        self.session.commit()
        return employee

    def delete(self, id: str):
        employee = self._get(id)
        self.session.delete(employee)
        self.session.commit()
