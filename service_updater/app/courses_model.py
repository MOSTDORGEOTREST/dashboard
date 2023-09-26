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
        return [(key, self.__dict__[key]) for key in self.__dict__.keys() if key != "user_id"]

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

        user_param = get_staff()

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