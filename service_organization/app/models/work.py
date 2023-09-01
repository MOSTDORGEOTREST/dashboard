from pydantic import BaseModel
from datetime import date
from enum import Enum

class WorkBase(BaseModel):
    employee_id: int
    date: date
    object_number: str
    count: float
    worktype_id: int

    class Config:
        orm_mode = True

class Work(WorkBase):
    work_id: int

class WorkCreate(WorkBase):
    pass

class WorkUpdate(WorkBase):
    pass

class WorkPrint(BaseModel):
    worktype_id: int
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
    worktype_id: int
    work_name: str
    category_name: WorkCategory
    price: float
    dev_tips: float

    class Config:
        orm_mode = True

class Report(BaseModel):
    date: date
    python_report: int
    python_dynamic_report: int
    python_compression_report: int
    mathcad_report: int
    physical_statement: int
    mechanics_statement: int
    python_all: float
    python_percent: float