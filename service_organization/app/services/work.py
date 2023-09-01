import datetime
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.dialects.postgresql import insert
from dateutil.relativedelta import relativedelta

from models.work import WorkCreate, WorkUpdate, WorkPrint, Report, Work
from models.staff import User
import db.tables as tables

class WorkService:
    def __init__(self, session: Session):
        self.session = session

    async def _get(self, id: int) -> Optional[tables.works]:
        work = await self.session.execute(
            select(tables.works).
            filter_by(work_id=id)
        )
        work = work.scalars().first()
        if not work:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return work

    async def get(self, id: int) -> tables.works:
        return await self._get(id)

    async def create(self, data: WorkCreate) -> tables.works:
        stmt = insert(tables.works).returning(tables.works.work_id).values(
            **data.dict())
        id = await self.session.execute(stmt)
        await self.session.commit()
        return tables.works(work_id=id, **data.dict())

    async def update(self, id: str, data: WorkUpdate) -> tables.works:
        work = self._get(id)

        q = update(tables.works).where(tables.works.work_id == id).values(
            **data.dict()
        )
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()
        return Work(work_id=id, **data.dict())

    async def delete(self, id: str):
        q = delete(tables.works).where(tables.works.work_id == id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()

    async def get_work_types(self) -> Optional[tables.worktypes]:
        worktypes = await self.session.execute(
            select(tables.worktypes)
        )
        worktypes = worktypes.scalars().all()
        return worktypes

    async def get_month_work(self, month: int, year: int, user_id: int = None, category: str = None) -> list:
        """Все работы за задынный месяц для конкретного сотрудника"""
        filters = []

        if user_id:
            filters.append(tables.works.employee_id == user_id)
        if category:
            filters.append(tables.worktypes.category_name == category)

        work = await self.session.execute(
            select(
                tables.works.work_id,
                tables.works.date,
                tables.works.object_number,
                tables.works.count,
                tables.works.worktype_id,
                tables.worktypes.work_name,
                tables.worktypes.price
            ).
            join(
                tables.worktypes,
                tables.worktypes.worktype_id == tables.works.worktype_id,
                isouter=True
            ).
            filter(extract('month', tables.works.date) == month).
            filter(extract('year', tables.works.date) == year).
            filter(*filters).
            order_by(extract('day', tables.works.date))
        )
        q = work.fetchall()
        l = []

        for item in q:
            l.append(WorkPrint(
                worktype_id=item[0],
                date=item[1],
                object_number=item[2],
                count=item[3],
                work_id=item[4],
                work_name=item[5],
                price=item[6],
            ))
        return l

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

    async def dev_pay_calc(self, pay_all, developer_percent):
        """"""
        pays = await self.session.execute(
            select(tables.worktypes)
        )
        pays = pays.scalars().all()

        tips = {}
        for pay in pays:
            if pay.dev_tips != 0:
                tips[pay.work_name] = pay.dev_tips

        get = lambda d, key: d[key]["count"] if d.get(key, None) else 0

        dev_pay = 0

        for tip in tips:
            dev_pay += get(pay_all, tip) * tips[tip]

        return dev_pay * (developer_percent / 100)

    async def get_base_pay(self, month: int, year: int, rate: float) -> float:
        """Расчет базовой зарплаты через ставку и премию"""
        prize = await self.session.execute(
            select(tables.prizes).
            filter_by(date=datetime.date(year=year, month=month, day=25))
        )
        prize = prize.scalars().first()
        prize = prize.value if prize else 0
        return round((prize/100 + 1) * rate * 1000, 2)

    async def get_month_user_pay(self, user, month: int, year: int) -> dict:
        report_works = await self.get_month_work(month=month, year=year, user_id=user.employee_id, category="Протоколы и ведомости")
        report_works_pay = self.work_calc(report_works)

        courses_works = await self.get_month_work(month=month, year=year, user_id=user.employee_id, category="Курсы")
        courses_works_pay = self.work_calc(courses_works)

        calculations_works = await self.get_month_work(month=month, year=year, user_id=user.employee_id, category="Расчеты")
        calculations_works_pay = self.work_calc(calculations_works)

        pay = {
            "reports": report_works_pay,
            "courses": courses_works_pay,
            "calculations": calculations_works_pay,
            "base": await self.get_base_pay(month=month, year=year, rate=user.rate)
        }

        general_pay = pay["base"]

        for key in report_works_pay:
            general_pay += report_works_pay[key]["payment"]

        for key in courses_works_pay:
            general_pay += courses_works_pay[key]["payment"]

        for key in calculations_works_pay:
            general_pay += calculations_works_pay[key]["payment"]

        if user.developer_percent:
            works_all = await self.get_month_work(month=month, year=year)
            pay_all = self.work_calc(works_all)
            pay["developer"] = await self.dev_pay_calc(pay_all, user.developer_percent)
            general_pay += pay["developer"]
        else:
            pay["developer"] = 0

        pay["general"] = general_pay

        return pay

    async def get_month_reports(self, month: int, year: int) -> Report:
        report_works = await self.get_month_work(month=month, year=year, category="Протоколы и ведомости")

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

    async def get_reports(self, month_period: int) -> List[Report]:
        res = []
        for i in range(month_period):
            current_date = datetime.date.today() - relativedelta(months=i)
            reports = await self.get_month_reports(month=current_date.month, year=current_date.year)
            res.append(reports)
        return res[::-1]

    async def get_pays(self, month_period: int, user) -> dict:
        res = {}
        for i in range(month_period):
            current_date = datetime.date.today() - relativedelta(months=i)
            res[current_date] = await self.get_month_user_pay(user, month=current_date.month, year=current_date.year)
        return res

    async def check_exsistance(self, data: WorkCreate):
        work = await self.session.execute(
            select(tables.works).
            filter_by(
                object_number=data.object_number,
                work_id=data.work_id,
                count=data.count
            )
        )
        work = work.scalars().first()
        if not work:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return work.date




















