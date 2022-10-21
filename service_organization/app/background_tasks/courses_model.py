from dataclasses import dataclass
from openpyxl import load_workbook

@dataclass
class UnitCourses:
    """Класс хранит одну строчку с курсами"""
    user_id: int = None
    technical_administration: int = 0
    infrastructure_administration: int = 0
    contract_administration: int = 0
    technical_support: int = 0
    lecture: int = 0
    another: int = 0
    calculation: int = 0

    def __repr__(self):
        return "\n".join([f'{el[0]}: {el[1]}' for el in self.get_work()])

    def get_work(self):
        return [(key, self.__dict__[key]) for key in self.__dict__.keys()]


class XlsBookCourses:
    """
    Convenience class for xlrd xls reader (only read mode)
    Note: Methods imputes operates with Natural columns and rows indexes
    """

    book = None
    sheet = 'Учет курсов'
    def __init__(self, path: str):
        self.set_book(path)

    def set_book(self, path: str):
        assert path.endswith('.xlsx'), 'Template should be .xlsx file format'
        self.book = load_workbook(path, data_only=True)

    def cell_value(self, column: str, row: int):
        return self.book[self.sheet][f"{column}{row}"].value

    def cell_value_int(self, column: str, row: int) -> int:
        value = self.cell_value(column, row)
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def get_data(self):
        works = []

        cell_param = {
            'G': 'technical_administration',
            'H': 'infrastructure_administration',
            'I': 'contract_administration',
            'J': 'technical_support',
            'K': 'lecture',
            'M': 'another',
            'N': 'calculation'
        }

        user_param = {
            'Палашина М.Д.': 13,
            'Смирнов Д.А.': 5,
            'Сергиенко В.В.': 33,
            'Тишин Н.Р.': 2,
            'Денисова Л.Г.': 11,
            'Жмылев Д.А.': 8,
            'Селиванова О.С.': 34,
            'Михайлова Е.В.': 37,
            'Шарунова А.А.': 20,
            'Горшков Е.С.': 6,
            'Доронин С.А.': 36,
        }

        for row in range(2, 500):
            user = self.cell_value('F', row)
            if user:
                unit = UnitCourses(user_id=user_param[user])
                for column in cell_param.keys():
                    val = self.cell_value_int(column, row)
                    if val:
                        setattr(unit, cell_param[column], val)
                works.append(unit)
        return works






if __name__ == "__main__":
    a = XlsBookCourses("/Users/mac1/Desktop/projects/10.Октябрь_2022_Учет техподдержки.xlsx")
    print(a.get_data())