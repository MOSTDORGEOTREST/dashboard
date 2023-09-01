from pydantic import BaseModel
from datetime import date

class BaseUser(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    phone_number: int
    birthday: date
    is_superuser: bool
    rate: int
    developer_percent: float

class UserCreate(BaseUser):
    password: str

class UserUpdate(BaseUser):
    password: str

    def to_dict(self):
        return self.__dict__

class LowUser(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    phone_number: int
    birthday: date

class User(BaseUser):
    employee_id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

