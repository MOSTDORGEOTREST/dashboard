import datetime
from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from io import BytesIO
from datetime import date
import asyncio
import aioschedule
import emoji
import openai
import translators.server as tss
from langdetect import detect

from functions import save_json_prize, read_json_prize, get_respones, get_respones_with_auth, \
    download_content_as_bytes, str_pay, get_auth
from config import configs
from massages import Massages
from utils import States


bot = Bot(token=configs.API_TOKEN)
openai.api_key = configs.OPENAI_TOKEN
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


saved_prize = read_json_prize()


users_logins = {}


@dp.message_handler(state=States.STATE_1)
async def first_state_case_met(message: types.Message):
    users_logins[message.from_user.id] = {
        'username': message.text,
        'password': None
    }
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(States.all()[2])
    await message.reply('Введите пароль:', reply=False)


@dp.message_handler(state=States.STATE_2)
async def second_state_case_met(message: types.Message):
    users_logins[message.from_user.id]['password'] = message.text
    register = await get_auth(
            username=users_logins[message.from_user.id]['username'],
            password=users_logins[message.from_user.id]['password']
        )

    if register is None:
        await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
        return

    if 'detail' in register:
        users_logins.pop(message.from_user.id)
        await message.answer("Неправильный логин или пароль " + emoji.emojize(":smiling_face_with_tear:"))
    else:
        users_logins[message.from_user.id]['id'] = register["id"]
        await message.answer(emoji.emojize("Успешная авторизация\nДля доступа к выплатам используйте команду /pay"))

    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()


@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    await message.answer(Massages.start_massage())


@dp.message_handler(commands=["prize"])
async def prize(message: types.Message):
    """Запрос текущей премии"""
    today = date.today()
    prize = await get_respones(f'{configs.SERVER_URI}/prizes/{today.year}-{today.month}-25')
    if prize is None:
        await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
        return

    await message.answer(f"{prize.get('value', 0)} %")


@dp.message_handler(commands=["prizes"])
async def prizes(message: types.Message):
    """Запрос истории премий"""
    prizes = await get_respones(f'{configs.SERVER_URI}/prizes/')
    if prizes is None:
        await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
        return

    try:
        s = "".join([f"дата: {prize['date']} | премия: {prize['value']}\n" for prize in prizes])
        await message.answer(s if s else "Не найдено")
    except:
        await message.answer("Не найдено")


@dp.message_handler(commands=["report"])
async def report(message: types.Message):
    """Запрос отчета за текущий месяц"""
    report = await get_respones(f'{configs.SERVER_URI}/works/report')
    if report is None:
        await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
        return

    if 'detail' in report:
        await message.answer("Не найдено")
    else:
        s = "\n".join([f"{key}: {report[key]}" for key in report.keys() if key != "date"])
        await message.answer(s)


@dp.message_handler(commands=["reports"])
async def reports(message: types.Message):
    """Запрос истории отчетности"""
    reports = await get_respones(f'{configs.SERVER_URI}/works/reports?month_period=6')
    if reports is None:
        await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
        return

    try:
        s = ""
        for report in reports:
            s += "\n".join([f"{key}: {report[key]}" for key in report.keys()]) + "\n\n\n"
        await message.answer(s if s else "Не найдено")
    except:
        await message.answer("Не найдено")


@dp.message_handler(commands=["pay"])
async def pay(message: types.Message):
    """Запрос оплаты за тукущий месяц"""
    user = users_logins.get(message.from_user.id, None)

    if not user:
        state = dp.current_state(user=message.from_user.id)
        await state.set_state(States.all()[1])
        await message.answer("Для этого запроса нужна авторизация, введите имя пользователя:")
        return
    else:
        pay = await get_respones_with_auth(
            url=f'{configs.SERVER_URI}/works/pay/{str(user["id"])}',
            username=user['username'],
            password=user['password']
        )

        if pay is None:
            await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
            return

        if 'detail' in pay:
            users_logins.pop(message.from_user.id)
            state = dp.current_state(user=message.from_user.id)
            await state.set_state(States.all()[1])
            await message.answer("Для этого запроса нужна авторизация, введите имя пользователя:")
        else:
            s = str_pay(pay)
            await message.answer(s)


@dp.message_handler(commands=["pays"])
async def pays(message: types.Message):
    """Запрос статистики оплаты"""
    pays = await get_respones_with_auth(f'{configs.SERVER_URI}/works/pays?month_period=6')
    if pays is None:
        await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
        return

    try:
        s = ""
        for pay in pays:
            s += "\n".join([f"{date}: {pay[date]['developer']}" for date in pay.keys()]) + "\n"
        await message.answer(s if s else "Не найдено")
    except:
        await message.answer("Не найдено")


@dp.message_handler(commands=["birthdays"])
async def birthdays(message: types.Message):
    """Запрос дней рождений в текущем месяцу"""
    today = date.today()
    staffs = await get_respones(f'{configs.SERVER_URI}/staff/month_birthday/?month={today.month}')
    if staffs is None:
        await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
        return

    try:
        s = ""
        for staff in staffs:
            s += f"{staff['birthday']} | {staff['full_name']}" + "\n\n"
        await message.answer(s if s else "Не найдено")
    except:
        await message.answer("Не найдено")


@dp.message_handler(commands=["time"])
async def time(message: types.Message):
    """Запрос текущего времени"""
    await message.answer(datetime.datetime.now())


@dp.message_handler()
async def echo(message: types.Message):
    if message.text.upper().find('НОМЕР') != -1:
        name = message.text.split(" ")[1]
        staffs = await get_respones(f'{configs.SERVER_URI}/staff/{name}')

        if staffs is None:
            await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
            return

        try:
            s = "".join([f"{staff['full_name']} | {staff['phone_number']}\n" for staff in staffs])
            await message.answer(s if s else "Не найдено")
        except:
            await message.answer("Не найдено")

    elif message.text.upper().find('ЗАКАЗЧИК') != -1:
        name = message.text.split(" ")[1]

        customers = await get_respones(f'{configs.SERVER_CUSTOMER_URI}/customers/{name}')

        if customers is None:
            await message.answer(text="Сервер не отвечает " + emoji.emojize(":smiling_face_with_tear:"))
            return

        if len(customers):
            for customer in customers:
                s = f"ФИО: {customer['full_name']}\nНомер телефона: +{customer['phone_number']}\nПочта: {customer['email']}\nОрганизация: {customer['organization']}\nДата рождения: {customer['birthday']}\n"
                photo = await download_content_as_bytes(f'{configs.SERVER_CUSTOMER_URI}/customers/get_photo/{customer["id"]}')
                try:
                    bytes_photo = BytesIO()
                    bytes_photo.write(photo)
                    bytes_photo.seek(0)
                    await bot.send_photo(message.from_user.id, types.InputFile(bytes_photo), caption=s)
                except utils.exceptions.BadRequest:
                    await message.answer(s)
        else:
            await message.answer("Не найдено")

    elif message.text.upper() == "НЕТ" and massage.from_user.id == configs.MDGT_CHAT_ID:
        await message.reply("Пидора ответ")

    elif "chatGPT" in message.text:
        text = message.text.replace("chatGPT", "")

        lang = detect(text)

        if lang != "en":
            text = tss.google(text, 'ru', 'en')

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )

        if lang != "en":
            answer = tss.google(response["choices"][0]["text"].replace("\n", ""), 'en', 'ru')
        else:
            answer = response["choices"][0]["text"].replace("\n", "")

        await message.reply(answer)


async def scheduler():

    async def check_prize():
        global saved_prize
        today = date.today()
        prize = await get_respones(f'{configs.SERVER_URI}/prizes/{today.year}-{today.month}-25')
        try:
            prize = prize.get('value', 0)
            if prize != saved_prize:
                if prize == 0 and today.day != 1:
                    pass
                else:
                    saved_prize = prize
                    save_json_prize(prize)
                    await bot.send_message(configs.MDGT_CHANNEL_ID, text=Massages.prize_massage(prize))
        except TypeError:
            pass

    async def check_birthday():
        today = date.today()
        staffs = await get_respones(f'{configs.SERVER_URI}/staff/day_birthday/?month={today.month}&day={today.day}')
        try:
            for staff in staffs:
                if staff == "detail":
                    return
                await bot.send_message(configs.MDGT_CHANNEL_ID,
                                      text=Massages.happy_birthday_massage(staff["full_name"], staff["phone_number"]))
        except TypeError:
            pass

    aioschedule.every(20).minutes.do(check_prize)
    aioschedule.every().day.at("9:30").do(check_birthday)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=False,
        on_startup=on_startup,
        on_shutdown=shutdown
    )