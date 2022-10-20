import os
from tqdm import tqdm
import re
from dataclasses import dataclass
import datetime
import xlrd
from xlrd import open_workbook

@dataclass
class Unit:
    """Класс хранит одну строчку с выданными протоколами и ведомостями по объекту"""
    object_number: str = None
    engineer: str = "unknown"
    mathcad_report: int = 0
    python_compression_report: int = 0
    python_report: int = 0
    python_dynamic_report: int = 0
    plaxis_report: int = 0
    physical_statement: int = 0
    mechanics_statement: int = 0

    def __repr__(self):
        return f"\n\t\t\tОбъект: {self.object_number}, Исполнитель: {self.engineer}," \
               f" Протоколы: Маткад - {self.mathcad_report}, Python Компрессия - {self.python_compression_report}," \
               f" Python Другое - {self.python_report}, Python Динамика - {self.python_dynamic_report}," \
               f" Plaxis - {self.plaxis_report};" \
               f" Ведомости: Механика - {self.mechanics_statement}, Физика - {self.physical_statement}"

    def get_reports(self):
        return {'mathcad_report': self.mathcad_report, 'python_compression_report': self.python_compression_report,
                'python_report': self.python_report, 'python_dynamic_report': self.python_dynamic_report,
                'plaxis_report': self.plaxis_report, 'physical_statement': self.physical_statement,
                'mechanics_statement': self.mechanics_statement}

    def get_work(self):
        work = self.get_reports()
        res = []
        for key in [
            'mathcad_report',
            'python_compression_report',
            'python_report',
            'python_dynamic_report',
            'plaxis_report',
            'physical_statement',
            'mechanics_statement'
        ]:
            if work[key] != 0:
                if key == 'plaxis_report':
                    res.append(['python_report', work[key]])
                res.append([key, work[key]])
        return res


class XlsBook:
    """
    Convenience class for xlrd xls reader (only read mode)
    Note: Methods imputes operates with Natural columns and rows indexes
    """

    book = None
    sheet = None

    __sheet_index: int

    def __init__(self, path: str):
        self.set_book(path)

    def set_book(self, path: str):
        assert path.endswith('.xls'), 'Template should be .xls file format'
        self.book = open_workbook(path, formatting_info=True)
        self.set_sheet_by_index(0)

    def set_sheet_by_index(self, index: int):
        self.sheet = self.book.sheet_by_index(index)
        self.__sheet_index = index

    def set_next_sheet(self):
        _last_sheet_index = self.sheet_count() - 1
        if self.__sheet_index < _last_sheet_index:
            self.set_sheet_by_index(self.__sheet_index + 1)

    def is_empty_sheet(self, min_cols: int = 1, min_rows: int = 1) -> bool:
        if self.sheet.ncols < min_cols or self.sheet.nrows < min_rows:
            return True
        return False

    def get_sheet_index(self) -> int:
        return self.__sheet_index

    def sheet_count(self) -> int:
        return len(self.book.sheet_names())

    def sheet_names(self) -> list:
        return self.book.sheet_names()

    def cell_value(self, natural_row: int, natural_column: int):
        return self.sheet.cell(natural_row - 1, natural_column - 1).value

    def cell_value_int(self, natural_row: int, natural_column: int) -> int:
        value = self.cell_value(natural_row, natural_column)
        try:
            return int(value)
        except ValueError:
            return 0

    def cell_value_date(self, natural_row: int, natural_column: int):
        MARKS = ['/', ' ', ',']

        value = str(self.cell_value(natural_row, natural_column))

        if not value.replace(' ', ''):
            return None

        if self.cell_value_int(natural_row, natural_column):
            value = self.cell_value_int(natural_row, natural_column)
            return xlrd.xldate_as_datetime(value, 0)

        for mark in MARKS:
            if mark in value:
                value = value.replace(mark, '.')

        if re.fullmatch(r'[0-9]{2}[.][0-9]{2}[.][0-9]{4}', value):
            try:
                return datetime.strptime(value, '%d.%m.%Y').date()
            except ValueError:
                pass
        if re.fullmatch(r'[0-9]{2}[.][0-9]{2}[.][0-9]{2}', value):
            try:
                return datetime.strptime(value, '%d.%m.%y').date()
            except ValueError:
                pass

        return None

    def cell_back_color(self, natural_row: int, natural_column: int):
        row = natural_row - 1
        col = natural_column - 1
        cell = self.sheet.cell(row, col)
        xf = self.book.xf_list[cell.xf_index]
        if not xf.background:
            return None
        return self.__get_color(xf.background.pattern_colour_index)

    def cell_front_color(self, natural_row: int, natural_column: int):
        row = natural_row - 1
        col = natural_column - 1
        cell = self.sheet.cell(row, col)
        xf = self.book.xf_list[cell.xf_index]
        font = self.book.font_list[xf.font_index]
        if not font:
            return None
        return self.__get_color(font.colour_index)

    def __get_color(self, color_index: int):
        return self.book.colour_map.get(color_index)


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
        start_date = datetime.datetime(year=2022, month=1, day=1)

        last_date = None
        '''last defined in xls date is the last date overall'''

        def next_month(_date):
            month = _date.month
            if month + 1 == 13:
                return datetime.datetime(year=_date.year + 1, month=1, day=1)
            return datetime.datetime(year=_date.year, month=month + 1, day=1)

        def prev_month(_date):
            month = _date.month
            if month - 1 == 0:
                return datetime.datetime(year=_date.year - 1, month=12, day=1)
            return datetime.datetime(year=_date.year, month=month - 1, day=1)

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

        _now = datetime.datetime.now()
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


    excel_path = '/Users/mac1/Desktop/projects/ПРОТОКОЛЫ+ведомости.xls'

    if not os.path.exists(excel_path):
        raise FileNotFoundError("Отсутствует файл отчетов")

    statment_data = read_excel_statment(excel_path)

    for work in tqdm(get_works(statment_data)):
        try:
            print(work)
            # create(data=work)
        except:
            pass


if __name__ == "__main__":
    report_parser()
    #prize_parser(settings.prize_directory)
