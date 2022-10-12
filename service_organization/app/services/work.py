import datetime
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract
from dateutil.relativedelta import relativedelta

from models.work import WorkCreate, WorkUpdate, WorkPrint, Report
from models.staff import User
import db.tables as tables
from db.database import get_session


class WorkService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get(self, id: int) -> Optional[tables.Work]:
        work = self.session.query(tables.Work).filter_by(id=id).first()
        if not work:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return work

    def get(self, id: int) -> tables.Work:
        work = self._get(id)
        return work

    def create(self, data: WorkCreate) -> tables.Work:
        work = tables.Work(
            **data.dict()
        )
        self.session.add(work)
        self.session.commit()
        return work

    def update(self, id: str, data: WorkUpdate) -> tables.Work:
        work = self._get(id)
        for field, value in data:
            setattr(work, field, value)
        self.session.commit()
        return work

    def delete(self, id: str):
        work = self._get(id)
        self.session.delete(work)
        self.session.commit()

    def get_month_work(self, month: int, year: int, user_id: int = None, category: str = None) -> list:
        """Все работы за задынный месяц для конкретного сотрудника"""
        filters = []

        if user_id:
            filters.append(tables.Work.user_id == user_id)
        if category:
            filters.append(tables.WorkType.category == category)

        q = (
            self.session
            .query(
                tables.Work,
                tables.WorkType.work_name,
                tables.WorkType.price)
            .join(
                tables.WorkType,
                tables.WorkType.id == tables.Work.work_id,
                isouter=True)
            .filter(extract('month', tables.Work.date) == month)
            .filter(extract('year', tables.Work.date) == year)
            .filter(*filters)
            .order_by(extract('day', tables.Work.date))
            .all()
        )

        l = []

        for item in q:
            l.append(WorkPrint(
                id=item[0].id,
                date=item[0].date,
                object_number=item[0].object_number,
                work_name=item[1],
                count=item[0].count,
                price=item[2],
                work_id=item[0].work_id
            ))
        return l

    def get_month_user_pay(self, user, month: int, year: int) -> dict:
        report_works = self.get_month_work(month=month, year=year, user_id=user.id, category="Протоколы и ведомости")
        report_works_pay = self.work_calc(report_works)

        courses_works = self.get_month_work(month=month, year=year, user_id=user.id, category="Курсы")
        courses_works_pay = self.work_calc(courses_works)

        pay = {
            "reports": report_works_pay,
            "courses": courses_works_pay,
            "base": self.get_base_pay(month=month, year=year, rate=user.rate)
        }

        general_pay = pay["base"]

        if user.calculation_percent or user.developer_percent:
            works_all = self.get_month_work(month=month, year=year)
            pay_all = self.work_calc(works_all)
            pay["developer"] = self.dev_pay_calc(pay_all, user.developer_percent)

        pay["general"] = general_pay

        return pay

    def get_work_types(self) -> Optional[tables.WorkType]:
        return self.session.query(tables.WorkType).all()

    def get_base_pay(self, month: int, year: int, rate: float) -> float:
        """Расчет базовой зарплаты через ставку и премию"""
        prize = self.session.query(tables.Prize).filter_by(date=datetime.date(year=year, month=month, day=25)).first()
        prize = prize.value if prize else 0
        return round((prize/100 + 1) * rate, 2)

    def work_calc(self, works) -> dict:
        """Подсчет работ по категориям"""
        res = {}
        for work in works:
            if res.get(work.work_name):
                res[work.work_name]["count"] += work.count
                res[work.work_name]["payment"] += work.count * work.price
            else:
                res[work.work_name] = {
                    "count": work.count,
                    "payment": work.price * work.count
                }
        return res

    def dev_pay_calc(self, pay_all, developer_percent):
        """"""
        pays = self.session.query(tables.WorkType).filter(tables.WorkType.dev_tips != 0).all()

        tips = {
            pay.work_name: pay.dev_tips for pay in pays
        }

        get = lambda d, key: d[key]["count"] if d.get(key, None) else 0

        dev_pay = 0

        for tip in tips:
            dev_pay += get(pay_all, tip) * tips[tip]

        return dev_pay * (developer_percent / 100)

    def get_month_reports(self, month: int, year: int) -> Report:
        report_works = self.get_month_work(month=month, year=year, category="Протоколы и ведомости")

        python_report = 0
        python_dynamic_report = 0
        python_compression_report = 0
        mathcad_report = 0
        physical_statement = 0
        mechanics_statement = 0

        for report in report_works:
            if report.work_name == "Протокол python":
                python_report += report.count
            elif report.work_name == "Протокол по динамике python":
                python_dynamic_report += report.count
            elif report.work_name == "Протокол по компрессии python":
                python_compression_report += report.count
            elif report.work_name == "Ведомость физика":
                physical_statement += report.count
            elif report.work_name == "Ведомость механика":
                mechanics_statement += report.count
            elif report.work_name == "Протокол mathcad":
                mathcad_report += report.count

        python_all = python_report + python_compression_report + python_dynamic_report
        python_percent = round((python_all / (python_all + mathcad_report)) * 100, 2) if python_all + mathcad_report != 0 else 100

        return Report(
            date=datetime.date(year=year, month=month, day=25),
            python_report=python_report,
            python_dynamic_report=python_dynamic_report,
            python_compression_report=python_compression_report,
            mathcad_report=mathcad_report,
            physical_statement=physical_statement,
            mechanics_statement=mechanics_statement,
            python_all=python_all,
            python_percent=python_percent,
        )

    def get_reports(self, month_period: int) -> List[Report]:
        res = []
        for i in range(month_period):
            current_date = datetime.today() - relativedelta(months=i)
            res.append(self.get_month_reports(month=current_date.month, year=current_date.year))
        return res

    def get_month_pay(self, month: int, year: int) -> dict:
        pay = self.get_month_user_pay(
            user=User(
                id=1,
                full_name='Тишин Никита Романович',
                phone_number=79096562200,
                birthday=datetime.date.today(),
                is_superuser=True,
                rate=1,
                developer_percent=100,
                calculation_percent=100
            ),
            month=month,
            year=year
        )
        return {
            'developer': pay["developer"]
        }

    def get_pays(self, month_period: int) -> List[Report]:
        res = []
        for i in range(month_period):
            current_date = datetime.today() - relativedelta(months=i)
            res.append(self.get_month_pay(month=current_date.month, year=current_date.year))
        return res




















