from datetime import datetime, date, timedelta
from dateutil import rrule
from passlib.hash import bcrypt
import openpyexcel
import os
from db.database import Session
import xlrd
from loguru import logger
import time
from tqdm import tqdm

from models.work import Work, WorkCreate
from background_tasks.statment_model import XlsBook, Unit
from background_tasks.courses_model import XlsBookCourses, UnitCourses
from models.prize import Prize
import db.tables as tables
from db.tables import Base
from db.database import engine
from settings import settings

def staff_parser():
    try:
        wb = openpyexcel.load_workbook(settings.excel_staff)
        for i in tqdm(range(2, 50)):
            name = wb["Лист1"]['B' + str(i)].value
            if name is not None:
                name = name.strip()
                id = int(wb["Лист1"]['A' + str(i)].value)
                password = wb["Лист1"]['C' + str(i)].value
                phone_number = int(wb["Лист1"]['D' + str(i)].value) if wb["Лист1"]['F' + str(i)].value is not None else None
                birthday = wb["Лист1"]['E' + str(i)].value
                is_superuser = True if int(wb["Лист1"]['F' + str(i)].value) else False
                rate = wb["Лист1"]['G' + str(i)].value
                developer_percent = wb["Лист1"]['H' + str(i)].value
                calculation_percent = wb["Лист1"]['I' + str(i)].value

                session = Session()
                get = session.query(tables.Staff).filter_by(full_name=name).first()
                session.close()

                if not get:
                    session = Session()
                    session.add(tables.Staff(
                        id=id,
                        full_name=name,
                        password_hash=bcrypt.hash(password),
                        phone_number=phone_number,
                        birthday=birthday,
                        is_superuser=is_superuser,
                        rate=rate,
                        developer_percent=developer_percent,
                        calculation_percent=calculation_percent
                    ))
                    session.commit()
                    session.close()

    except Exception as err:
        logger.error("Ошибка создания базы пользователей " + str(err))

def work_types_parser():
    try:
        wb = openpyexcel.load_workbook(settings.excel_work_types)
        for i in tqdm(range(2, 50)):
            name = wb["Лист1"]['A' + str(i)].value
            if name:
                price = wb["Лист1"]['C' + str(i)].value
                category = wb["Лист1"]['B' + str(i)].value
                dev_tips = wb["Лист1"]['D' + str(i)].value
                id = int(wb["Лист1"]['E' + str(i)].value)
                session = Session()
                get = session.query(tables.WorkType).filter_by(work_name=name).first()
                if not get:
                    session = Session()
                    session.add(
                        tables.WorkType(
                            id=id,
                            work_name=name,
                            price=price,
                            dev_tips=dev_tips,
                            category=category
                        )
                    )
                    session.commit()
                session.close()

    except Exception as err:
        logger.error("Ошибка создания базы типов работ " + str(err))

def prize_parser(current_date: date = date.today()):

    def get_current_prize(excel_directory, current_date):
        mounth, year = current_date.strftime('%m'), "20" + current_date.strftime('%y')

        try:
            path = os.path.join(
                f'{excel_directory}{year}',
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

    def _get(date: date) -> tables.Prize:
        session = Session()
        prize = session.query(tables.Prize).filter_by(date=date).first()
        session.close()
        return prize

    def update(data: Prize) -> None:
        session = Session()
        prize = session.query(tables.Prize).filter_by(date=data.date).first()
        for field, value in data:
            setattr(prize, field, value)
        session.commit()
        session.close()

    def create(data: Prize) -> None:
        session = Session()
        session.add(tables.Prize(**data.dict()))
        session.commit()
        session.close()

    excel_directory = settings.prize_directory

    if not os.path.exists(excel_directory):
        raise FileNotFoundError("Отсутствует файл премии")

    _excel_directory = excel_directory

    base_prize = _get(date(year=current_date.year, month=current_date.month, day=25))

    if not base_prize:
        _prize = 0.0
    else:
        _prize = base_prize.prize

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
            current_path = names(str(d.year), int(d.month))
            assert os.path.exists(current_path), f"Не существует файла {current_path}"
            book = XlsBookCourses(current_path)

            for item in book.get_data():
                try:
                    reoports = item.get_work()
                except TypeError:
                    continue

                for report in reoports:
                    work_name, count = report

                    yield WorkCreate(
                        user_id=item.user_id,
                        date=date,
                        object_number="",
                        work_id=work_dict[work_name],
                        count=count)

    def create(data: WorkCreate) -> None:
        session = Session()
        session.add(tables.Work(**data.dict()))
        session.commit()
        session.close()

    for work in tqdm(get_works()):
        try:
            create(data=work)
        except:
            pass


def report_parser():
    def get_works(main_data):
        user_dict = {
            'Баранов С.С.': 18,
            'Денисова Л.Г.': 11,
            'Жмылёв Д.А.': 8,
            'Михайлов А.И.': 9,
            'Михайлова Е.В.': 37,
            'Михалева О.В.': 22,
            'Селиванова О.С.': 34,
            'Семенова О.В.': 15,
            'Сергиенко В.В.': 33,
            'Тишин Н.Р.': 2,
            'Чалая Т.А.': 17,
            'Шарунова А.А.': 20,
            'Орлов М.С.': 38,
            'Савенков Д.В.': 39,
        }

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
                        user_id=user_dict[unit.engineer.strip()],
                        date=date,
                        object_number=unit.object_number,
                        work_id=work_dict[work_name],
                        count=count
                    )

                    '''if datetime:
                        from_db = _get(
                            user_id=user_dict[unit.engineer.strip()],
                            date=date,
                            object_number=unit.object_number,
                            work_id=work_dict[work_name],
                            count=count
                        )
                        if not from_db:
                            yield WorkCreate(
                                user_id=user_dict[unit.engineer.strip()],
                                date=date,
                                object_number=unit.object_number,
                                work_id=work_dict[work_name],
                                count=count
                            )
                        else:
                            continue
                    else:
                        yield WorkCreate(
                            user_id=user_dict[unit.engineer.strip()],
                            date=date,
                            object_number=unit.object_number,
                            work_id=work_dict[work_name],
                            count=count
                        )'''

    def _get(
            user_id: int,
            date: date,
            object_number: str,
            work_id: int,
            count: int
    ) -> tables.Work:
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
                _sheet_ind = _sheet_names.index(str(_start_year))
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

    def create(data: WorkCreate) -> None:
        session = Session()
        session.add(tables.Work(**data.dict()))
        session.commit()
        session.close()

    excel_path = settings.statment_excel_path

    if not os.path.exists(excel_path):
        raise FileNotFoundError("Отсутствует файл отчетов")

    statment_data = read_excel_statment(excel_path)

    for work in tqdm(get_works(statment_data)):
        try:
            create(data=work)
        except:
            pass

def parser(deelay=None):

    def f():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        prize_dates = [
            date(year=dt.year, month=dt.month, day=25) for dt in rrule.rrule(
                rrule.MONTHLY, dtstart=date(2020, 5, 1), until=date.today()
            )]

        for d_p in tqdm(prize_dates):
            try:
                prize_parser(d_p)
            except Exception as err:
                logger.error("Ошибка обновления премии " + str(err))

        try:
            staff_parser()
            logger.info("successful update staff")
        except Exception as err:
            logger.error("Ошибка обновления сотрудников " + str(err))

        try:
            work_types_parser()
            logger.info("successful update work types")
        except Exception as err:
            logger.error("Ошибка обновления типов работ " + str(err))

        try:
            report_parser()
            logger.info("successful update reports")
        except Exception as err:
            logger.error("Ошибка обновления отчетов " + str(err))

        try:
            courses_parser()
            logger.info("successful update courses")
        except Exception as err:
            logger.error("Ошибка обновления курсов " + str(err))

    if not deelay:
        f()
    else:
        while True:
            time.sleep(deelay)
            f()


if __name__ == "__main__":
    from settings import settings
    #parser(settings.prize_directory, settings.statment_excel_path)
    #report_parser()
    staff_parser()
    #prize_parser(settings.prize_directory)
