
from openpyxl import load_workbook

def get_staff(full=False):
    wb = load_workbook("/Users/mac1/Desktop/projects/dashboard/data/staff.xlsx")
    result = {}
    for i in range(2, 50):
        name = wb["Лист1"]['B' + str(i)].value
        if name is not None:
            if full:
                result[name.strip()] = int(wb["Лист1"]['A' + str(i)].value)
            else:
                name = name.strip().split(" ")
                result[f"{name[0]} {name[1][0]}.{name[2][0]}."] = int(wb["Лист1"]['A' + str(i)].value)
    return result


b = get_staff()
a = {
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
    'Фролова Н.А.': 35
}

