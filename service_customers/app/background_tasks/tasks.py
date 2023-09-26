import openpyexcel
import os
from db.database import Session
from loguru import logger
import time
from db.tables import Base
from db.database import engine

from settings import settings
import db.tables as tables
from tqdm import tqdm

def parser(deelay=86400):
    time.sleep(deelay)
    while True:
        try:
            update_db()
            logger.info("База заказчиков обновлена")
        except:
            pass

        time.sleep(deelay)

def update_db():
    if not os.path.exists(settings.excel_file):
        raise FileNotFoundError("Отсутствует файл заказчиков")

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    try:
        wb = openpyexcel.load_workbook(settings.excel_file)
        for i in tqdm(range(2, len(wb["Лист1"]['B']) + 1)):
            id = wb["Лист1"]['A' + str(i)].value
            full_name = wb["Лист1"]['B' + str(i)].value
            phone_number = wb["Лист1"]['C' + str(i)].value
            email = wb["Лист1"]['D' + str(i)].value
            birthday = wb["Лист1"]['E' + str(i)].value
            organization = wb["Лист1"]['F' + str(i)].value
            sex = wb["Лист1"]['G' + str(i)].value
            level = wb["Лист1"]['H' + str(i)].value

            if full_name is not None and id:
                session = Session()
                session.add(tables.Customers(
                    id=id,
                    full_name=full_name,
                    phone_number=phone_number,
                    email=email,
                    birthday=birthday,
                    organization=organization,
                    sex=sex,
                    level=level
                ))
                session.commit()
                session.close()

    except Exception as err:
            logger.error("Ошибка создания базы заказчиков" + str(err))


if __name__ == "__main__":
    from settings import settings
    #parser(settings.prize_directory, settings.statment_excel_path)
    report_parser(settings.statment_excel_path)
    #prize_parser(settings.prize_directory)
