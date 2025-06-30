import os
import time
from dataclasses import dataclass
from datetime import date
from typing import Optional, Union, List
from dateutil import rrule
import xlrd
import openpyxl

from app.config import configs
from app.db import Session, engine
from app.db import tables


def read_excel_cell(path: str, sheet_name: str, row: int, col: int) -> Union[str, float, None]:
    """
    Читает значение ячейки из Excel-файла (.xls или .xlsx)

    :param path: Путь к Excel-файлу
    :param sheet_name: Название листа
    :param row: Номер строки (0-индексация)
    :param col: Номер колонки (0-индексация)
    :return: Значение ячейки (str, float, None и т.п.)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")

    if path.lower().endswith(".xls"):
        workbook = xlrd.open_workbook(path)
        sheet = workbook.sheet_by_name(sheet_name)
        return sheet.cell(row, col).value

    elif path.lower().endswith(".xlsx"):
        workbook = openpyxl.load_workbook(path, data_only=True)
        sheet = workbook[sheet_name]
        cell = sheet.cell(row=row + 1, column=col + 1)  # openpyxl — 1-индексация
        return cell.value

    else:
        raise ValueError("Формат файла должен быть .xls или .xlsx")

def find_excel_file(directory: str, year: str, month: str) -> str:
    """
    Возвращает путь к существующему Excel-файлу (.xlsx или .xls)

    :param directory: Базовая директория с Excel-файлами (str)
    :param year: Год, например '2025'
    :param month: Месяц, например '06'
    :return: Путь к найденному Excel-файлу (str)
    :raises FileNotFoundError: если файл не найден
    """
    base_filename = f"{month}.{year} - Учет офисного времени"
    year_dir = os.path.join(directory, year)

    candidates: List[str] = [
        os.path.join(year_dir, f"{base_filename}.xlsx"),
        os.path.join(year_dir, f"{base_filename}.xls"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    checked = "\n".join(candidates)
    raise FileNotFoundError(f"Excel-файл не найден. Проверены пути:\n{checked}")


@dataclass
class PrizeData:
    date: date
    value: float


class PrizeParser:
    def __init__(self, excel_directory: str):
        self.excel_directory = excel_directory

        if not os.path.exists(self.excel_directory):
            raise FileNotFoundError("Отсутствует директория премий")

    def get_month_prize_from_excel(self, month: str, year: str) -> float:
        excel_file  = find_excel_file(
            directory=self.excel_directory,
            year=year,
            month=month
        )

        prize_raw = read_excel_cell(
            path=excel_file,
            sheet_name='Итог',
            row=0,
            col=24
        )

        if str(prize_raw).lower() in {"xxx", "ххх"}:
            raise ValueError("Неверная запись")

        return prize_raw

    def db_parse(self, current_date: date) -> Optional[PrizeData]:
        """
        Обновляет запись премии в БД, если она изменилась
        :param current_date: Дата, за которую проверяется премия
        :return: PrizeData если обновление произошло, иначе None
        """
        month = current_date.strftime('%m')
        year = "20" + current_date.strftime('%y')

        prize = self.get_month_prize_from_excel(
            month=month,
            year=year
        )
        prize_date = date(
            year=current_date.year,
            month=current_date.month,
            day=25
        )

        existing = self._db_get(prize_date)

        if existing is None or prize > existing.value:
            data = PrizeData(date=prize_date, value=prize)
            if existing:
                self._db_update(data)
            else:
                self._db_create(data)
            return data

        return None

    def daemon(self, general_update: bool = True):
        """
            Функция для непрерывного парсинга премий и сопутствующих данных
            :param excel_dir: Путь к директории с Excel-файлами
            :param delay_seconds: Задержка между итерациями. Если None — выполняется один раз.
            :param use_db: Нужно ли писать в БД
            """
        if general_update:
            try:
                tables.works.__table__.drop(engine)
                tables.works.__table__.create(engine)
            except Exception as err:
                print("⚠️ Ошибка при сбросе таблицы works:", err)

            prize_dates = [
                date(year=dt.year, month=dt.month, day=25)
                for dt in rrule.rrule(
                    rrule.MONTHLY, dtstart=date(2020, 5, 1), until=date.today()
                )
            ]

            try:
                for d in prize_dates:
                    self.db_parse(d)
                    print(f"✅ Премия за {d} успешно обновлена")
            except Exception as err:
                print("⚠️ Ошибка при обновлении премий:", err)
        else:
            today = date.today()
            date(year=today.year, month=today.month, day=25)

    def _db_get(self, prize_date: date) -> Optional[PrizeData]:
        session = Session()
        record = session.query(tables.prizes).filter_by(date=prize_date).first()
        session.close()

        return PrizeData(date=record.date, value=record.value) if record else None

    def _db_update(self, data: PrizeData) -> None:
        session = Session()
        prize = session.query(tables.prizes).filter_by(date=data.date).first()
        prize.date = data.date
        prize.value = data.value
        session.commit()
        session.close()

    def _db_create(self, data: PrizeData) -> None:
        session = self.Session()
        session.add(self.tables.prizes(**data.__dict__))
        session.commit()
        session.close()




if __name__ == "__main__":
    parser = PrizeParser(
        excel_directory="Z:\МДГТ - (Учет рабоч. времени, Отпуск, Даты рожд., телефоны, план работ, Исполнители)/УЧЕТ рабочего времени/",
    )
    month = date.today().strftime('%m')
    year = "20" + date.today().strftime('%y')

    record = parser.get_month_prize_from_excel(month='06', year='2023')
    print(record)

    parser.prize_daemon(general_update=True)