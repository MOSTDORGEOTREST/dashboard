from pydantic import BaseSettings

conf = ['server', 'linux', 'mac']

config = conf[2]

if config == 'server':
    db_path = "/databases/organization/"
elif config == 'linux':
    db_path = "/home/tnick/databases/organization/"
elif config == 'mac':
    db_path = "/Users/mac1/Desktop/projects/databases/organization/"


class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8500

    excel_staff: str = f'{db_path}staff.xlsx'
    excel_work_types: str = f'{db_path}work_types.xlsx'
    database_url: str = f"sqlite:///{db_path}control.sqlite3"

settings = Settings()