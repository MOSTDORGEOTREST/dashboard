from typing import List, Optional
from datetime import date
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract
from sqlalchemy import func

from models.staff import Staff
import db.tables as tables
from db.database import get_session

class StaffService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get(self, id: int) -> Optional[tables.Staff]:
        staffs = self.session.query(tables.Staff).filter_by(id=id).first()

        if not staffs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        return staffs

    def get_all(self) -> List[tables.Staff]:
        return self.session.query(tables.Staff).order_by(tables.Staff.full_name).all()

    def get_month_birthday(self, month) -> List[tables.Staff]:
        return self.session.query(tables.Staff).filter(extract('month', tables.Staff.birthday) == month).order_by(tables.Staff.full_name).all()

    def get_day_birthday(self, month, day) -> List[tables.Staff]:
        print("krgboi")
        return self.session.query(tables.Staff).filter(extract('month', tables.Staff.birthday) == month).filter(extract('day', tables.Staff.birthday) == day).order_by(tables.Staff.full_name).all()

    def get(self, name) -> Optional[tables.Staff]:
        staffs = self.session.query(tables.Staff).all()

        if not staffs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        res = []

        for staff in staffs:
            if name in staff.full_name:
                res.append(staff)

        return res

    def create(self, staff_data: Staff) -> tables.Staff:
        staff = tables.Staff(
            **staff_data.dict())
        self.session.add(staff)
        self.session.commit()
        return staff

    def update(self, id: int, staff_data: Staff) -> tables.Staff:
        staff = self._get(id)
        for field, value in staff_data:
            setattr(staff, field, value)
        self.session.commit()
        return staff

    def delete(self, id: str):
        staff = self._get(id)
        self.session.delete(staff)
        self.session.commit()
