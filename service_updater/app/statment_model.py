import re
from dataclasses import dataclass
from datetime import datetime
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
                    continue
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