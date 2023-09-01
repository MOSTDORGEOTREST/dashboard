from typing import List, Optional
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from models.prize import Prize
import db.tables as tables

class PrizesService:
    def __init__(self, session: Session):
        self.session = session

    async def _get(self, date: date) -> Optional[tables.prizes]:
        prize = await self.session.execute(
            select(tables.prizes).
            filter_by(date=date)
        )
        prize = prize.scalars().first()
        if not prize:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return prize

    async def get_all(self) -> List[tables.prizes]:
        prizes = await self.session.execute(
            select(tables.prizes)
        )
        prizes = prizes.scalars().all()
        return prizes

    async def get(self, date: date) -> tables.prizes:
        return await self._get(date)

    async def create(self, prize_data: Prize) -> tables.prizes:
        stmt = insert(tables.prizes).values(
            **prize_data.dict())

        stmt = stmt.on_conflict_do_update(
            index_elements=['date'],
            set_=stmt.excluded
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return tables.prizes(**prize_data.dict())

    async def update(self, date: date, prize_data: Prize) -> tables.prizes:
        prize = self._get(date)
        prize = prize.scalars().first()

        if not prize:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        q = update(tables.prizes).where(tables.prizes.date == date).values(
            value=prize_data.value
        )
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()
        return Prize(
            **prize_data.dict()
        )

    async def delete(self, date: date):
        q = delete(tables.prizes).where(tables.prizes.date == date)
        q.execution_options(synchronize_session="fetch")

        await self.session.execute(q)
        await self.session.commit()

    def create_many(self, prizes_data: List[Prize]) -> List[tables.prizes]:
        prizes = [tables.Report(**prize_data.dict()) for prize_data in prizes_data]
        self.session.add_all(prizes)
        self.session.commit()
        return prizes
