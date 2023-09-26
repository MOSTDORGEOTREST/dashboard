from pydantic import BaseSettings

conf = ['server', 'linux', 'mac']

config = conf[0]

if config == 'server':
    db_path = "/databases/organization/"
    db_copy_dir = "/files/Обмен/Никите Романовичу/db/"
elif config == 'linux':
    db_path = "/home/tnick/databases/organization/"
    db_copy_dir = "/run/user/1000/gvfs/smb-share:server=192.168.0.1,share=files//Обмен/Никите Романовичу/db/"
elif config == 'mac':
    db_path = "/Users/mac1/Desktop/projects/databases/organization/"
    db_copy_dir = "/Users/mac1/Desktop/projects/databases"


class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8500

    database_url: str = f"sqlite:///{db_path}control.sqlite3"
    database_file = f"{db_path}control.sqlite3"
    db_copy_dir = db_copy_dir


settings = Settings()