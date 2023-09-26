from pydantic import BaseModel
from datetime import date

class ReportBase(BaseModel):
    object_number: str
    object_name: str
    laboratory_number: str
    test_type: str

    class Config:
        orm_mode = True

class Report(ReportBase):
    id: int
    date: date

class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass
