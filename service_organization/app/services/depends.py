from db.database import async_session
from services.staff import UsersService
from services.prize import PrizesService
from services.work import WorkService

async def get_users_service():
    async with async_session() as session:
        async with session.begin():
            yield UsersService(session)

async def get_prizes_service():
    async with async_session() as session:
        async with session.begin():
            yield PrizesService(session)

async def get_works_service():
    async with async_session() as session:
        async with session.begin():
            yield WorkService(session)
