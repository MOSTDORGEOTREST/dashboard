import datetime
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import hashlib

from models.reports import Report, ReportCreate, ReportUpdate
import db.tables as tables
from db.database import get_session


class ReportService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get(self, id: int) -> Optional[tables.Reports]:
        report = self.session.query(tables.Reports).filter_by(id=id).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return report

    def get(self, id: int) -> tables.Reports:
        report = self._get(id)
        return report

    def create(self, data: ReportCreate) -> tables.Reports:
        id = hashlib.sha1(f"{data.object_number} {data.laboratory_number} {data.test_type}".encode("utf-8")).hexdigest()

        try:
            report = self._get(id)
            self.update(id, data)
        except HTTPException:
            report = tables.Reports(
                id=id,
                date=datetime.date.today(),
                **data.dict()
            )
            self.session.add(report)
            self.session.commit()
            return report

    def update(self, id: str, data: ReportUpdate) -> tables.Reports:
        report = self._get(id)
        for field, value in data:
            setattr(report, field, value)
        setattr(report, "date", datetime.date.today())
        self.session.commit()
        return report

    def delete(self, id: str):
        report = self._get(id)
        self.session.delete(report)
        self.session.commit()

    def get_object(self, object_number) -> List[tables.Reports]:
        q = (
            self.session
            .query(
                tables.Reports)
            .filter(tables.Reports.object_number == object_number)
            .all()
        )
        return q

    def get_objects(self):
        query = self.session.query(tables.Reports.object_number.distinct().label("title"))
        q = [row.title for row in query.all()]
        return q






