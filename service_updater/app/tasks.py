from datetime import date
from dateutil import rrule
from pydantic import BaseModel
import os
import xlrd
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
#from models.work import Work, WorkCreate
#from background_tasks.statment_model import XlsBook, Unit
#from background_tasks.courses_model import XlsBookCourses, UnitCourses
import tables as tables
from config import configs
from statment_model import XlsBook, Unit
from courses_model import XlsBookCourses

engine = create_engine(
    configs.database_url
)

Session = sessionmaker(
    engine,
    autocommit=False,
    autoflush=False
)
class Prize(BaseModel):
    date: date
    value: float

    class Config:
        orm_mode = True

class WorkCreate(BaseModel):
    employee_id: int
    date: date
    object_number: str
    count: float
    worktype_id: int

    class Config:
        orm_mode = True

def get_staff(full=False):
    short_staff = {'Никитин Н.М.': 1, 'Тишин Н.Р.': 2, 'Шкарова О.П.': 3, 'Смирнов Д.А.': 4, 'Горшков Е.С.': 5,
                   'Власов С.В.': 6, 'Жмылев Д.А.': 7, 'Михайлов А.И.': 8, 'Селиванов И.А.': 9,
                   'Денисова Л.Г.': 10, 'Палашина М.Д.': 11, 'Васильева О.Н.': 112, 'Семенова О.В.': 13,
                   'Паршикова Е.В.': 14, 'Чалая Т.А.': 15, 'Баранов С.С.': 16, 'Ботнарь Д.Г.': 17,
                   'Шарунова А.А.': 18, 'Озмидов О.Р.': 19, 'Михалева О.В.': 20, 'Белоусов К.Ю.': 21,
                   'Хайбулина Е.М.': 22, 'Череповский А.В.': 23, 'Жидков И.М.': 24, 'Старостин П.А.': 25,
                   'Щербинина Н.В.': 26, 'Абдуллина Н.А.': 27, 'Сорокина О.В.': 28, 'Байбекова С.Р.': 29,
                   'Сергиенко В.В.': 30, 'Селиванова О.С.': 31, 'Фролова Н.А.': 32, 'Доронин С.А.': 33,
                   'Михайлова Е.В.': 34, 'Орлов М.С.': 35, 'Савенков Д.В.': 36}
    full_staff = {'Никитин Никита Михайлович': 1, 'Тишин Никита Романович': 2, 'Шкарова Оксана Павловна': 3,
                  'Смирнов Дмитрий Александрович': 5, 'Горшков Евгений Сергеевич': 6, 'Власов Сергей Викторович': 7,
                  'Жмылев Дмитрий Александрович': 8, 'Михайлов Артем Игоревич': 9, 'Селиванов Иван Алексеевич': 10,
                  'Денисова Людмила Геннадьевна': 11, 'Палашина Марина Дмитриевна': 13,
                  'Васильева Ольга Николаевна': 14, 'Семенова Ольга Васильевна': 15,
                  'Паршикова Елена Владимировна': 16, 'Чалая Татьяна Анатольевна': 17,
                  'Баранов Семен Сергеевич': 18, 'Ботнарь Дмитрий Григорьевич': 19, 'Шарунова Анна Андреевна': 20,
                  'Озмидов Олег Ростиславович': 21, 'Михалева Ольга Владимировна': 22,
                  'Белоусов Константин Юрьевич': 23, 'Хайбулина Евгения Михайловна': 24,
                  'Череповский Александр Викторович': 25, 'Жидков Илья Михайлович': 26,
                  'Старостин Павел Алексеевич': 28, 'Щербинина Надежда Владимировна': 29,
                  'Абдуллина Надежда Алексеевна': 30, 'Сорокина Оксана Владимировна': 31,
                  'Байбекова Светлана Равилевна': 32, 'Сергиенко Валерия Викторовна': 33,
                  'Селиванова Олеся Сергеевна': 34, 'Фролова Наталья Александровна': 35,
                  'Доронин Станислав Александрович': 36, 'Михайлова Елена Владимировна': 37,
                  'Орлов Михаил Сергеевич': 38, 'Савенков Дмитрий Витальевич': 39}

    if full:
        return full_staff
    else:
        return short_staff

def prize_parser(current_date: date = date.today()):

    def get_current_prize(excel_directory, current_date):
        mounth, year = current_date.strftime('%m'), "20" + current_date.strftime('%y')
        try:
            path = os.path.join(
                f'{excel_directory}', str(year),
                f'{mounth}.{year} - Учет офисного времени.xls')

            if os.path.exists(path):
                with xlrd.open_workbook(path) as workbook:
                    worksheet = workbook.sheet_by_name('Итог')
                    prize = worksheet.cell(0, 24).value
                if prize == "ххх" or prize == "xxx":
                    prize = 0.0
                else:
                    prize = float(prize)
            else:
                prize = 0.0
        except:
            prize = 0.0

        return prize

    def update_run(excel_dir, base_prize, current_date):
        prize = get_current_prize(excel_dir, current_date)
        if prize > base_prize:
            data = {
                "date": date(year=current_date.year, month=current_date.month, day=25),
                "value": prize,
            }

            prize_data = Prize(**data)

            test = _get(date=prize_data.date)

            if test is not None:
                update(data=prize_data)
            else:
                create(data=prize_data)

    def _get(date: date) -> tables.prizes:
        session = Session()
        prize = session.query(tables.prizes).filter_by(date=date).first()
        session.close()
        return prize

    def update(data: Prize) -> None:
        session = Session()
        prize = session.query(tables.prizes).filter_by(date=data.date).first()
        for field, value in data:
            setattr(prize, field, value)
        session.commit()
        session.close()

    def create(data: Prize) -> None:
        session = Session()
        session.add(tables.prizes(**data.dict()))
        session.commit()
        session.close()

    excel_directory = configs.prize_directory

    if not os.path.exists(excel_directory):
        raise FileNotFoundError("Отсутствует файл премии")

    _excel_directory = excel_directory

    base_prize = _get(date(year=current_date.year, month=current_date.month, day=25))

    if not base_prize:
        _prize = 0.0
    else:
        _prize = base_prize.value

    update_run(_excel_directory, _prize, current_date)

def courses_parser():
    work_dict = {
        'technical_administration': 7,
        'infrastructure_administration': 8,
        'contract_administration': 9,
        'technical_support': 10,
        'lecture': 11,
        'another': 12,
        'calculation': 13
    }

    def names(month, year):
        names = {
            1: f'1.Январь_{year}_Учет техподдержки.xlsx',
            2: f'2.Февраль_{year}_Учет техподдержки.xlsx',
            3: f'3.Март_{year}_Учет техподдержки.xlsx',
            4: f'4.Апрель_{year}_Учет техподдержки.xlsx',
            5: f'5.Май_{year}_Учет техподдержки.xlsx',
            6: f'6.Июнь_{year}_Учет техподдержки.xlsx',
            7: f'7.Июль_{year}_Учет техподдержки.xlsx',
            8: f'8.Август_{year}_Учет техподдержки.xlsx',
            9: f'9.Сентябрь_{year}_Учет техподдержки.xlsx',
            10: f'10.Октябрь_{year}_Учет техподдержки.xlsx',
            11: f'11.Ноябрь_{year}_Учет техподдержки.xlsx',
            12: f'12.Декабрь_{year}_Учет техподдержки.xlsx',
        }
        return names[month]

    def get_works():
        dates = [
            date(year=dt.year, month=dt.month, day=1) for dt in rrule.rrule(
                rrule.MONTHLY, dtstart=date(2022, 1, 1), until=date.today()
            )]

        for d in dates:
            current_path = f"{configs.courses_directory}{str(d.year)}/{names(int(d.month), str(d.year))}"
            if not os.path.exists(current_path):
                continue
            book = XlsBookCourses(current_path)

            for item in book.get_data():
                try:
                    reoports = item.get_work()
                except TypeError:
                    continue

                for report in reoports:
                    work_name, count = report
                    if not count:
                        continue
                    yield WorkCreate(
                            employee_id=item.user_id,
                            date=date(year=d.year, month=d.month, day=25),
                            object_number="-",
                            worktype_id=work_dict[work_name],
                            count=count
                        )

    def bulk(data_list: list) -> None:
        session = Session()
        session.bulk_save_objects(data_list)
        session.commit()
        session.close()

    works = []

    for work in get_works():
        works.append(tables.works(**work.dict()))

    bulk(works)

def report_parser():
    def get_works(main_data):

        user_dict = get_staff()

        work_dict = {
            'mathcad_report': 6,
            'python_compression_report': 3,
            'python_report': 1,
            'python_dynamic_report': 2,
            'physical_statement': 4,
            'mechanics_statement': 5
        }

        dates = main_data.keys()

        for date in dates:
            for unit in main_data[date]:
                try:
                    reoports = unit.get_work()
                except TypeError:
                    continue

                if not unit.engineer.strip():
                    continue

                if unit.object_number == 'СуммапротоколовкромеPythonДинамика':
                    continue

                for report in reoports:
                    work_name, count = report
                    yield WorkCreate(
                        employee_id=user_dict[unit.engineer.strip().replace("ё", "е")],
                        date=date,
                        object_number=unit.object_number,
                        worktype_id=work_dict[work_name],
                        count=count
                    )

    def _get(
            user_id: int,
            date: date,
            object_number: str,
            work_id: int,
            count: int
    ) -> tables.works:
        session = Session()
        report = session.query(tables.Work).filter_by(
            user_id=user_id,
            date=date,
            object_number=object_number,
            work_id=work_id,
            count=count
        ).first()
        session.close()
        return report

    def read_excel_statment(path: str) -> 'ReportParser.data':
        __result: 'ReportParser.data' = {}
        result: 'ReportParser.data' = {}

        # colors
        YELLOW = (255, 255, 0)

        # program local columns shifts (natural local column - 'Object' column): 2 - 1 = 1 and so on
        # reports
        MATHCAD = 1  # Mathcad
        PYTHON_COMPRESSION = 2  # Python Компрессия
        PYTHON = 3  # Python Другое
        PYTHON_DYNAMIC = 4  # Python Динамика
        PLAXIS = 5  # Plaxis
        # Statements
        MECHANICS = 6  # Механика
        PHYSICAL = 7  # Физика

        # local columns per engineer
        N_COLS = 9  # count from 1
        '''cols count per engineer'''

        # first month row
        START_ROW = 6

        # if no last date in xls start date will be used
        start_date = datetime(year=2022, month=1, day=1)

        last_date = None
        '''last defined in xls date is the last date overall'''

        def next_month(_date):
            month = _date.month
            if month + 1 == 13:
                return datetime(year=_date.year + 1, month=1, day=1)
            return datetime(year=_date.year, month=month + 1, day=1)

        def prev_month(_date):
            month = _date.month
            if month - 1 == 0:
                return datetime(year=_date.year - 1, month=12, day=1)
            return datetime(year=_date.year, month=month - 1, day=1)

        # load book
        book = XlsBook(path)

        # engineers
        engineers = []
        engineers_row = 1

        def engineer(natural_col: int):
            """Returns engineer name by natural column index"""
            __col = natural_col - 1
            if __col // N_COLS >= len(engineers):
                return None
            return engineers[__col // N_COLS]

        _now = datetime.now()
        _start_year = 2022
        _current_year = _now.year
        _sheet_names = book.sheet_names()
        _start_sheet_ind = _sheet_names.index(str(_start_year))
        book.set_sheet_by_index(_start_sheet_ind)
        # start parsing for each sheet
        while not book.is_empty_sheet(min_rows=START_ROW, min_cols=N_COLS):
            # count sheet sizes
            ncols = book.sheet.ncols + 1  # Natural ncols
            nrows = book.sheet.nrows + 1  # Natural nrows

            # fill-in engineers
            engineers = []
            for col in range(ncols):
                curr_engineer = book.cell_value(engineers_row, col).strip()
                if curr_engineer in engineers:
                    continue
                if len(curr_engineer) > 0 and curr_engineer.replace(' ', '') != '':
                    engineers.append(curr_engineer)
            if len(engineers) < 1:  # no engineers = no data
                return {}

            # for each row (read comments)
            for row in range(START_ROW, nrows):
                # search for date (YELLOW line)
                dates = [*__result.keys()]

                yellow_flag = False
                for yellow_col in range(1, ncols):
                    if book.cell_back_color(row, yellow_col) == YELLOW:
                        yellow_flag = True
                        break
                    yellow_flag = False

                if yellow_flag:
                    # save the last date
                    for col in range(1, ncols):
                        value = book.cell_value_date(row, col)
                        if value:
                            last_date = value

                    # fill in base dates to recalculate them later by last_date
                    if dates:
                        __result[next_month(dates[-1])] = []
                    else:
                        __result[start_date] = []
                    continue

                if not dates:
                    continue

                # skip the summarize row
                if book.cell_value(row, 1) == "Сумма":
                    continue

                # then parse columns per each engineer
                for col in range(1, ncols + 1, N_COLS):

                    assert type(book.cell_value(row, col)) != float, "ОШИБКА В ТИПЕ ДАННЫХ. ПРОВЕРЬ ШАБЛОН"

                    _object = book.cell_value(row, col).replace(' ', '')

                    # first one should find out if there any object (per each engineer)
                    if not engineer(col) or not _object:
                        continue

                    if col + MECHANICS > ncols:
                        continue

                    # read numbers (per each engineer)
                    _mathcad_count = book.cell_value_int(row, col + MATHCAD)
                    _python_compression_count = book.cell_value_int(row, col + PYTHON_COMPRESSION)
                    _python_count = book.cell_value_int(row, col + PYTHON)
                    _python_dynamic_count = book.cell_value_int(row, col + PYTHON_DYNAMIC)
                    _plaxis_count = book.cell_value_int(row, col + PLAXIS)
                    _mechanics_count = book.cell_value_int(row, col + MECHANICS)
                    _physical_count = book.cell_value_int(row, col + PHYSICAL)

                    # add to result (per each engineer)
                    __result[dates[-1]].append(Unit(object_number=str(_object), engineer=engineer(col),
                                                    mathcad_report=_mathcad_count,
                                                    python_compression_report=_python_compression_count,
                                                    python_report=_python_count,
                                                    python_dynamic_report=_python_dynamic_count,
                                                    plaxis_report=_plaxis_count, physical_statement=_physical_count,
                                                    mechanics_statement=_mechanics_count))

            # and next sheet
            if _current_year > _start_year:
                _start_year += 1
                ind = 2022 if _start_year == 2023 else _start_year
                _sheet_ind = _sheet_names.index(str(ind))
                book.set_sheet_by_index(_sheet_ind)
            else:
                break

        # recalculate dates
        if last_date:
            start_date = last_date

            for i in range(len(__result.keys())):
                start_date = prev_month(start_date)

            for date in __result.keys():
                if len([*result.keys()]) > 0:
                    result[next_month([*result.keys()][-1])] = __result[date]
                else:
                    result[next_month(start_date)] = __result[date]

        return result

    def bulk(data_list: list) -> None:
        session = Session()
        session.bulk_save_objects(data_list)
        session.commit()
        session.close()

    excel_path = configs.statment_excel_path

    if not os.path.exists(excel_path):
        raise FileNotFoundError("Отсутствует файл отчетов")

    statment_data = read_excel_statment(excel_path)

    reports = []

    for work in get_works(statment_data):
        try:
            reports.append(tables.works(**work.dict()))
        except:
            pass
    bulk(reports)

def parser(deelay=None):
    print("sf")
    def f():
        prize_dates = [
            date(year=dt.year, month=dt.month, day=25) for dt in rrule.rrule(
                rrule.MONTHLY, dtstart=date(2020, 5, 1), until=date.today()
            )]
        try:
            for i in prize_dates:
                prize_parser(i)
            print("successful update prizes")
        except Exception as err:
            print('prizes error ', err)

        tables.works.__table__.drop(engine)
        tables.works.__table__.create(engine)

        try:
            courses_parser()
            print("successful update courses")
        except Exception as err:
            print('courses error ', err)

        try:
            report_parser()
            print("successful update reports")
        except Exception as err:
            print('reports error ', err)

    if not deelay:
        f()
    else:
        while True:
            time.sleep(deelay)
            f()


if __name__ == "__main__":
    parser(1200)
