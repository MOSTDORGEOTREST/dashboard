from pydantic import BaseModel
from datetime import date
from enum import Enum

class WorkBase(BaseModel):
    user_id: int
    date: date
    object_number: str
    work_id: int
    count: float

    class Config:
        orm_mode = True

class Work(WorkBase):
    id: int

class WorkCreate(WorkBase):
    pass

class WorkUpdate(WorkBase):
    pass

class WorkPrint(BaseModel):
    id: int
    date: date
    object_number: str
    work_name: str
    work_id: int
    count: float
    price: float

class WorkCategory(str, Enum):
    REPORTS = "Протоколы и ведомости"
    COURSES = "Курсы"
    CALCULATIONS = "Расчеты"

class WorkType(BaseModel):
    id: int
    work_name: str
    category: WorkCategory
    price: float
    dev_tips: float

    class Config:
        orm_mode = True

