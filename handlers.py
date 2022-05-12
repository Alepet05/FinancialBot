from loader import dp, bot
from aiogram import types
import db
import re
import datetime


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    """Приветствует пользователя и заносит его в БД"""
    user_id = message.from_user.id
    if not db.check_user_exists(user_id):
        db.add_new_user(user_id)
    await message.answer('Добро пожаловать')

@dp.message_handler(commands=['add'])
async def add_expense(message: types.Message):
    """Добавляет расход пользователя в БД"""
    user_id = message.from_user.id
    msg_text = message.text

    # проверяем корректность введенной пользователем команды
    pattern = '/add (\d+) (.+)'
    if re.search(pattern, msg_text):
        price, category_input = re.findall(pattern, msg_text)[0] # если команда корректна, то findall вернет список типа [('расход', 'категория')]
    else:
        await message.answer("Неверно введена команда")
        return

    category = category_input if category_input in db.get_categories() else 'прочее' # определяем введенную пользователем категорию расхода
    
    db.add_expense(user_id, int(price), category)

    await message.answer(f"Внесен расход {price} руб. на {category}")

@dp.message_handler(commands=['expenses'])
async def get_last_expenses(message: types.Message):
    """Выводит последние N расходов (N вводится пользователем)"""
    user_id = message.from_user.id
    expenses_count = int(message.text.split()[-1]) # формат команды /expenses {кол-во расходов}

    answer_text = ''
    last_expenses = db.get_last_expenses(user_id, expenses_count)

    for expense in last_expenses:
        answer_text += f"* {expense[1]} руб. на {expense[0]}\n"

    await message.answer(answer_text)

@dp.message_handler(commands=['today'])
async def get_today_statistic(message: types.Message):
    """Выводит информацию о тратах пользователя за сегодня"""
    user_id = message.from_user.id
    date = datetime.datetime.now().strftime('%Y-%m-%d')

    today_expenses = db.get_today_expenses(user_id, date)
    today_base_expenses = db.get_today_base_expanses(user_id, date)
    day_limit = int(db.get_day_limit())

    answer_text = 'Расходы сегодня:\n\n'
    answer_text += f'Всего: {today_expenses} руб.\n'
    answer_text += f'Базовые: {today_base_expenses} руб. из {day_limit} руб.'

    await message.answer(answer_text)