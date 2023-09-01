from pydantic import BaseSettings, Field
import os
from dotenv import load_dotenv
import http.client

load_dotenv(dotenv_path=os.path.normpath(".env"))

def get_self_public_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()

statment_path = "/files/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)/ПРОТОКОЛЫ+ведомости.xls"
prize_dir = "/files/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)/УЧЕТ рабочего времени/"
courses_dir = "/files/КУРСЫ ПОВЫШЕНИЯ КВАЛИФИКАЦИИ МДГТ/1. Заявки, Регистрация слушателей, Учет Договоров/Выплаты по курсам/"

statment_path = "Z:/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)/ПРОТОКОЛЫ+ведомости.xls"
prize_dir = "Z:/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)/УЧЕТ рабочего времени/"
courses_dir = "Z:/КУРСЫ ПОВЫШЕНИЯ КВАЛИФИКАЦИИ МДГТ/1. Заявки, Регистрация слушателей, Учет Договоров/Выплаты по курсам/"

class Configs_docker_compose(BaseSettings):
    host_ip: str = get_self_public_ip()
    database_url: str = Field(..., env='DATABASE_URL')
    jwt_secret: str = Field(..., env='JWT_SECRET')
    jwt_algorithm: str = Field(..., env='JWT_ALGORITHM')
    jwt_expiration: int = Field(..., env='JWT_EXPIRATION')

    statment_excel_path: str = os.path.normpath(statment_path)
    prize_directory: str = os.path.normcase(prize_dir)
    courses_directory: str = os.path.normcase(courses_dir)

configs = Configs_docker_compose()
