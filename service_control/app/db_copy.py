import shutil
from datetime import datetime
import time
import os

from settings import settings

def copy_db():
    while True:
        if os.path.exists(settings.database_file):
            if os.path.exists(os.path.join(settings.db_copy_dir, f'{datetime.now().strftime("%d-%m-%Y")}.sqlite3')):
                print(f'{datetime.now().strftime("%d-%m-%Y")} db is already exist')
            else:
                try:
                    shutil.copy(
                        settings.database_file,
                        os.path.join(settings.db_copy_dir, f'{datetime.now().strftime("%d-%m-%Y")}.sqlite3')
                    )
                    print(f'Success db copy {datetime.now().strftime("%d-%m-%Y")}')
                except Exception as err:
                    print(str(err))
        else:
            print("Не найден файл бд")

        time.sleep(86400)