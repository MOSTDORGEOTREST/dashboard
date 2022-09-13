from pydantic import BaseModel
from datetime import date

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


class WorkType(BaseModel):
    id: int
    work_name: str
    category: str
    price: float
    dev_tips: float


    class Config:
        orm_mode = True

