from pydantic import BaseModel
from datetime import date

class Prize(BaseModel):
    date: date
    value: float

    class Config:
        orm_mode = True