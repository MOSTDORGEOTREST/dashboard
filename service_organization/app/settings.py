from pydantic import BaseSettings
import os

conf = ['server', 'linux', 'mac', 'win']

config = conf[0]

if config == 'server':
    statment_path = "/files/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)/ПРОТОКОЛЫ+ведомости.xls"
    prize_dir = "/files/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)/УЧЕТ рабочего времени/"
    db_path = "/databases/organization/"
    courses_dir = "/files/КУРСЫ ПОВЫШЕНИЯ КВАЛИФИКАЦИИ МДГТ/1. Заявки, Регистрация слушателей, Учет Договоров/Выплаты по курсам/"
elif config == 'linux':
    statment_path = "/run/user/1000/gvfs/smb-share:server=192.168.0.1,share=files/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)//ПРОТОКОЛЫ+ведомости.xls"
    prize_dir = "/run/user/1000/gvfs/smb-share:server=192.168.0.1,share=files/МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ)/УЧЕТ рабочего времени/"
    db_path = "/home/tnick/databases/organization/"
    courses_dir = "/run/user/1000/gvfs/smb-share:server=192.168.0.1,share=files/КУРСЫ ПОВЫШЕНИЯ КВАЛИФИКАЦИИ МДГТ/1. Заявки, Регистрация слушателей, Учет Договоров/Выплаты по курсам/"
elif config == 'mac':
    statment_path = "/Users/mac1/Desktop/projects/databases/ПРОТОКОЛЫ+ведомости.xls"
    prize_dir = "/Users/mac1/Desktop/projects/databases/prize/"
    db_path = "/Users/mac1/Desktop/projects/databases/organization/"
    courses_dir = "/Users/mac1/Desktop/projects/databases/courses/"


class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    statment_excel_path: str = os.path.normpath(statment_path)
    prize_directory: str = os.path.normcase(prize_dir)
    courses_directory: str = os.path.normcase(courses_dir)

    excel_staff: str = f'{db_path}staff.xlsx'
    excel_work_types: str = f'{db_path}work_types.xlsx'
    database_url: str = f"sqlite:///{db_path}database.sqlite3"

    jwt_secret: str = "OOIOIPSJFBSFBSBGBBSB"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3 #days

settings = Settings()