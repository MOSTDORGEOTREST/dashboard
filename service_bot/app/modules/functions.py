import json
import os
import aiohttp
import humanize

from config import configs

def save_json_prize(prize: float):
    """Сохраняет премию в  JSON"""
    with open("prize.json", 'w', encoding='utf-8') as file:
        json.dump({"prize": prize}, file)

def read_json_prize():
    """Читает JSON в словарь питон"""
    if os.path.exists("prize.json"):
        with open("prize.json", 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        return json_data["prize"]
    else:
        save_json_prize(0)
        return 0

async def get_respones(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()
    except (aiohttp.client_exceptions.ClientConnectorError, aiohttp.client_exceptions.ContentTypeError):
        return None

async def get_respones_with_auth(url: str, username: str, password: str):
    jar = aiohttp.CookieJar(unsafe=True)
    try:
        async with aiohttp.ClientSession(cookie_jar=jar) as session:
            res = await session.post(f'{configs.SERVER_URI}/staff/sign-in/',
                                     data={
                                         "username": username,
                                         "password": password,
                                         "grant_type": "password",
                                         "scope": "",
                                         "client_id": "",
                                         "client_secret": ""
                                     }, allow_redirects=False)
            await res.json()

            async with session.get(url) as resp:
                return await resp.json()
    except aiohttp.client_exceptions.ClientConnectorError:
        return None

async def get_auth(username: str, password: str):
    jar = aiohttp.CookieJar(unsafe=True)
    try:
        async with aiohttp.ClientSession(cookie_jar=jar) as session:
            res = await session.post(f'{configs.SERVER_URI}/staff/sign-in/',
                                     data={
                                         "username": username,
                                         "password": password,
                                         "grant_type": "password",
                                         "scope": "",
                                         "client_id": "",
                                         "client_secret": ""
                                     }, allow_redirects=False)
            await res.json()

            async with session.get(f'{configs.SERVER_URI}/staff/user/') as resp:
                return await resp.json()
    except aiohttp.client_exceptions.ClientConnectorError:
        return None

async def download_content_as_bytes(url: str) -> bytes:
    content = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                content = await response.read()
    except aiohttp.client_exceptions.ClientConnectorError:
        pass
    finally:
        return content

def str_pay(pay):
    get_pay_by_name = lambda pay_name: sum([pay[pay_name][x]["payment"] for x in pay[pay_name].keys()]) \
        if len(pay[pay_name]) else 0

    str_pay = {
        'Общая сумма': humanize.intcomma(int(pay["general"])),
        'Выплата за протоколы': humanize.intcomma(int(get_pay_by_name("reports"))),
        'Выплата за курсы': humanize.intcomma(int(get_pay_by_name("courses"))),
        'Выплата за разработку': humanize.intcomma(int(pay["developer"])),
        'Выплата за расчеты': humanize.intcomma(int(get_pay_by_name("calculations"))),
    }
    return "\n".join([f'{key}: {str_pay[key]}' for key in str_pay.keys()])