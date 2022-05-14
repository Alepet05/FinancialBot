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
    await message.answer(
        "Бот для учёта финансов\n\n"
        "Добавить расход: /add 100 продукты\n"
        "Расходы за сегодня: /today\n"
        "Расходы за текущий месяц: /month\n"
        "N последних внесенных расходов: /expenses 10\n"
        "Категории трат: /categories")

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
    command = message.text.split()
    expenses_count = int(command[-1]) if len(command) == 2 else 5 # формат команды /expenses {кол-во расходов}. По умолчанию выводится 5 последних расходов

    answer_text = ''
    last_expenses = db.get_last_expenses(user_id, expenses_count)

    if type(last_expenses) is list:
        for expense in last_expenses:
            answer_text += f"* {expense[1]} руб. на {expense[0]} {expense[2]}\n"
    else:
        answer_text = last_expenses
        
    await message.answer(answer_text)

@dp.message_handler(commands=['today'])
async def get_today_statistic(message: types.Message):
    """Выводит информацию о тратах пользователя за сегодня"""
    user_id = message.from_user.id
    date = datetime.datetime.now().strftime('%Y-%m-%d')

    today_expenses = db.get_today_expenses(user_id, date)
    today_base_expenses = db.get_today_base_expanses(user_id, date)
    day_limit = db.get_day_limit()

    await message.answer(
        'Расходы сегодня:\n\n'
        f'Всего: {today_expenses} руб.\n'
        f'Базовые: {today_base_expenses} руб. из {day_limit} руб.'
    )

@dp.message_handler(commands=['week'])
async def get_week_statistic(message: types.Message):
    """Выводит информацию о тратах пользователя за текущую неделю"""
    user_id = message.from_user.id

    months = {
        '01': 31,
        '02': 28,
        '03': 31,
        '04': 30,
        '05': 31,
        '06': 30,
        '07': 31,
        '08': 31,
        '09': 30,
        '10': 31,
        '11': 30,
        '12': 31,
    }
    
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    year, month, day = current_date.split('-')
    # если мы в первой неделе месяца
    if int(day) <= 7:
        # если текущий месяц не январь
        if int(month) != 1:
            prev_month = int(month)-1 # получаем предыдущий месяц
            month_days_amount = months[prev_month] # получаем кол-во дней в предыдущем месяце
            zeroes_count = '0' if prev_month < 10 else '' # добавляем нуль, если нужно
            first_day_week = int(month_days_amount)-(7-int(day)) # определяем первый день текущей недели
            start_week = f"{year}-{zeroes_count}{prev_month}-{first_day_week}"
        # иначе текущий месяц - январь
        else:
            prev_month = 12 # очевидно, что в таком случае предыдущий месяц - декабрь прошлого года
            month_days_amount = months[prev_month]
            zeroes_count = '0' if prev_month < 10 else ''
            first_day_week = int(month_days_amount)-(7-int(day))
            start_week = f"{int(year)-1}-{zeroes_count}{prev_month}-{first_day_week}"
    else:
        first_day_week = int(day)-7
        zeroes_count = '0' if first_day_week < 10 else ''
        start_week = f"{year}-{month}-{zeroes_count}{first_day_week}"

    week_expenses = db.get_week_expenses(user_id, start_week, current_date)
    week_base_expenses = db.get_week_base_expenses(user_id, start_week, current_date)
    week_limit = db.get_week_limit()

    await message.answer(
        f'Расходы за текущую неделю (с {start_week} по {current_date}):\n\n'
        f'Всего: {week_expenses} руб.\n'
        f'Базовые: {week_base_expenses} руб. из {week_limit} руб.'
    )

@dp.message_handler(commands=['month'])
async def get_month_statistic(message: types.Message):
    """Выводит информацию о тратах пользователя за текущий месяц"""
    user_id = message.from_user.id

    # определяем начало текущего и следующего месяца 
    year, month, _ = datetime.datetime.now().strftime('%Y-%m-%d').split('-')
    current_month_date = f'{year}-{month}-01' # начало текущего месяца
    next_month = int(month)+1
    if next_month <= 12: # если укладываемся в год
        zeroes_count = '0' if next_month < 10 else '' # добавляем нуль, если нужно
        next_month_date = f'{year}-{zeroes_count}{month}-01'
    else: # иначе обновляем год
        next_month_date = f'{int(year)+1}-01-01'

    month_expenses = db.get_month_expenses(user_id, current_month_date, next_month_date)
    month_base_expenses = db.get_month_base_expenses(user_id, current_month_date, next_month_date)
    month_limit = db.get_month_limit()

    await message.answer(
        'Расходы за текущий месяц:\n\n'
        f'Всего: {month_expenses} руб.\n'
        f'Базовые: {month_base_expenses} руб. из {month_limit} руб.'
    )

@dp.message_handler(commands=['categories'])
async def get_categories(message: types.Message):
    categories = db.get_categories()
    answer_text = ''

    for category in categories:
        answer_text += f"* {category}\n"

    await message.answer(answer_text)