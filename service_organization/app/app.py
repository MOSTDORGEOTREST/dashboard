from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from db.database import Base, engine
from api import router
from config import configs
from db.database import async_session
from db import tables
from passlib.hash import bcrypt
from sqlalchemy.future import select
from sqlalchemy import update, delete

def create_ip_ports_array(ip: str, *ports):
    array = []
    for port in ports:
        array.append(f"{ip}:{str(port)}")
    return array

app = FastAPI(
    title="Georeport MDGT",
    description="Сервис аутентификации протоколов испытаний",
    version="2.3.0")

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:9573"]

origins += create_ip_ports_array(configs.host_ip, 3000, 8000, 80, 9573)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization", "Accept", "X-Requested-With"],
)

app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def index():
    return JSONResponse(content={'massage': 'successful'}, status_code=200)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def users():
        async with async_session() as session:
            async with session.begin():
                pas = {
                    'Никитин': "Fhb9F",
                    'Тишин': "F5Ev9",
                    'Шкарова': "nhDQ7",
                    'Смирнов': "YL33u",
                    'Горшков': "k95KR",
                    'Власов': "yEH8m",
                    'Жмылев': "7T3z5",
                    'Михайлов': "zg2Sj",
                    'Селиванов': "29wgR",
                    'Денисова': "Tj95Y",
                    'Палашина': "7RAxj",
                    'Васильева': "T7cb7",
                    'Семенова': "23wZH",
                    'Паршикова': "WZ8s5",
                    'Чалая': "hZGTd",
                    'Баранов': "gIwOV",
                    'Ботнарь': "PJwXN",
                    'Шарунова': "1Ia7r",
                    'Озмидов': "xzv9J",
                    'Михалева': "P7nGb",
                    'Белоусов': "M2gtY",
                    'Хайбулина': "hMziw",
                    'Череповский': "BgZ2U",
                    'Жидков': "VEsZ1",
                    'Старостин': "DnNQQ",
                    'Щербинина': "GZiuG",
                    'Абдуллина': "24Ukz",
                    'Сорокина': "Z6glX",
                    'Байбекова': "yl5cg",
                    'Сергиенко': "ETxUk",
                    'Селиванова': "VpFJM",
                    'Фролова': "98LkL",
                    'Доронин': "822Nt",
                    'Михайлова': "xHbzg",
                    'Орлов': "xhUYK",
                    'Савенков': "4nuzb"
                }

                user_names = await session.execute(
                    select(tables.staff)
                )
                user_names = user_names.scalars().all()

                for user in user_names:
                    q = update(tables.staff).where(tables.staff.employee_id == user.employee_id).values(
                        password_hash=bcrypt.hash(pas[user.last_name]),
                    )

                    q.execution_options(synchronize_session="fetch")
                    await session.execute(q)

                await session.commit()

    #await users()



