from pydantic import BaseModel
from datetime import date

class BaseUser(BaseModel):
    full_name: str
    phone_number: int
    birthday: date
    is_superuser: bool
    rate: int
    developer_percent: float
    calculation_percent: float

class UserCreate(BaseUser):
    password: str

class UserUpdate(BaseUser):
    password: str

class User(BaseUser):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

