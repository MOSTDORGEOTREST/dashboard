from pydantic import BaseSettings, Field
import os
from dotenv import load_dotenv
import http.client

load_dotenv(dotenv_path=os.path.normpath(".env"))

def get_self_public_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()

class Configs_docker_compose(BaseSettings):
    host_ip: str = get_self_public_ip()
    database_url: str = Field(..., env='DATABASE_URL')
    statment_excel_path: str = os.path.normpath("/files/ПРОТОКОЛЫ+ведомости.xls")
    prize_directory: str = os.path.normcase("/files/УЧЕТ рабочего времени/")
    courses_directory: str = os.path.normcase("/files/КУРСЫ ПОВЫШЕНИЯ КВАЛИФИКАЦИИ МДГТ/1. Заявки, Регистрация слушателей, Учет Договоров/Выплаты по курсам/")

class Configs(BaseSettings):
    host_ip: str = '37.139.85.41'
    database_url: str = ''
    statment_excel_path: str = 'C:/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)\ПРОТОКОЛЫ+ведомости.xls'
    prize_directory: str = r'C:/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)/УЧЕТ рабочего времени/'
    courses_directory: str = "Z:/КУРСЫ ПОВЫШЕНИЯ КВАЛИФИКАЦИИ МДГТ/1. Заявки, Регистрация слушателей, Учет Договоров/Выплаты по курсам/"

try:
    configs = Configs_docker_compose()
except:
    configs = Configs()
