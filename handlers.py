from loader import dp, bot
from aiogram import types
import users, categories, expenses, budget
import re
import datetime


def get_months(current_date: str):
    """Возвращает дату начала текущего и следующего месяцев

    Args:
        current_date (str): текущая дата пользователя

    Returns:
        tuple: кортеж дат начала текущего и следующего месяцев
    """
    year, month, _ = current_date.split('-')
    first_day_current_month = f'{year}-{month}-01' # начало текущего месяца
    next_month = int(month)+1
    if next_month <= 12: # если укладываемся в год
        zeroes_count = '0' if next_month < 10 else '' # добавляем нуль, если нужно
        first_day_next_month = f'{year}-{zeroes_count}{next_month}-01'
    else: # иначе обновляем год
        first_day_next_month = f'{int(year)+1}-01-01'

    return first_day_current_month, first_day_next_month

def get_start_week(current_date):
    """Возвращает дату начала текущей недели

    Args:
        current_date (str): текущая дата пользователя

    Returns:
        str: дата начала текущей недели
    """
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
    year, month, day = current_date.split('-')
    # если текущая дата это первая неделя месяца
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
            month_days_amount = months['12'] # очевидно, что в таком случае предыдущий месяц - декабрь прошлого года
            zeroes_count = '0' if prev_month < 10 else ''
            first_day_week = int(month_days_amount)-(7-int(day))
            start_week = f"{int(year)-1}-{zeroes_count}{prev_month}-{first_day_week}"
    else:
        first_day_week = int(day)-7
        zeroes_count = '0' if first_day_week < 10 else ''
        start_week = f"{year}-{month}-{zeroes_count}{first_day_week}"
    return start_week
    

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    """Приветствует пользователя и заносит его в БД"""
    user_id = message.from_user.id

    # регистрация пользователя
    if not users.check_user_exists(user_id):
        users.add_new_user(user_id)

    # инициализация бюджета пользователя
    budget.add_user_budget(user_id)

    await message.answer(
        "Бот для учёта финансов\n\n"
        "Добавить расход: /add 100 продукты\n"
        "Расходы за сегодня: /today\n"
        "Расходы за текущую неделю: /week\n"
        "Расходы за текущий месяц: /month\n"
        "N последних внесенных расходов: /expenses 10\n"
        "Категории расходов: /categories\n"
        "Статистика расходов по категориям за месяц: /statistics\n"
        "Изменить бюджет: /change нужные значения через пробел\n(по умолчанию 1000 руб./день, 4000 руб./нед., 15000 руб./мес.)")

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
        await message.answer("Неверно введена команда\nШаблон: /add трата категория")
        return

    category = category_input if category_input in categories.get_all_categories() else 'прочее' # определяем введенную пользователем категорию расхода
    
    expenses.add_expense(user_id, int(price), category)

    await message.answer(f"Внесен расход {price} руб. на {category}")

@dp.message_handler(commands=['expenses'])
async def get_last_expenses(message: types.Message):
    """Выводит последние N расходов (N вводится пользователем)"""
    user_id = message.from_user.id
    msg_text = message.text
    
    # проверяем корректность введенной пользователем команды
    pattern = '/expenses (\d+)'
    if re.search(pattern, msg_text):
        expenses_count = int(re.findall(pattern, msg_text)[0])
    else:
        await message.answer("Неверно введена команда\nШаблон: /expenses кол-во расходов")
        return 

    answer_text = ''
    last_expenses = expenses.get_last_expenses(user_id, expenses_count)

    if last_expenses:
        for expense in last_expenses:
            answer_text += f"* {expense[1]} руб. на {expense[0]} - {expense[2]}\n"
    else:
        answer_text = 'Отсутствуют какие-либо расходы'
        
    await message.answer(answer_text)

@dp.message_handler(commands=['today'])
async def get_today_statistics(message: types.Message):
    """Выводит информацию о тратах пользователя за сегодня"""
    user_id = message.from_user.id
    date = datetime.datetime.now().strftime('%Y-%m-%d')

    today_expenses = expenses.get_today_expenses(user_id, date)
    today_base_expenses = expenses.get_today_base_expanses(user_id, date)
    day_limit = budget.get_day_limit()

    await message.answer(
        'Расходы сегодня:\n\n'
        f'Всего: {today_expenses} руб.\n'
        f'Базовые: {today_base_expenses} руб. из {day_limit} руб.'
    )

@dp.message_handler(commands=['week'])
async def get_week_statistics(message: types.Message):
    """Выводит информацию о тратах пользователя за текущую неделю"""
    user_id = message.from_user.id
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_week = get_start_week(current_date)

    week_expenses = expenses.get_week_expenses(user_id, start_week, current_date)
    week_base_expenses = expenses.get_week_base_expenses(user_id, start_week, current_date)
    week_limit = budget.get_week_limit()

    await message.answer(
        f'Расходы за текущую неделю (с {start_week} по {current_date}):\n\n'
        f'Всего: {week_expenses} руб.\n'
        f'Базовые: {week_base_expenses} руб. из {week_limit} руб.'
    )

@dp.message_handler(commands=['month'])
async def get_month_statistics(message: types.Message):
    """Выводит информацию о тратах пользователя за текущий месяц"""
    user_id = message.from_user.id
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    first_day_current_month, first_day_next_month = get_months(current_date)

    month_expenses = expenses.get_month_expenses(user_id, first_day_current_month, first_day_next_month)
    month_base_expenses = expenses.get_month_base_expenses(user_id, first_day_current_month, first_day_next_month)
    month_limit = budget.get_month_limit()

    await message.answer(
        'Расходы за текущий месяц:\n\n'
        f'Всего: {month_expenses} руб.\n'
        f'Базовые: {month_base_expenses} руб. из {month_limit} руб.'
    )

@dp.message_handler(commands=['categories'])
async def get_categories(message: types.Message):
    """Выводит все категории в БД"""
    cats = categories.get_all_categories()
    answer_text = 'Доступные категории: \n\n'

    for category in cats:
        answer_text += f"* {category}\n"

    await message.answer(answer_text)

@dp.message_handler(commands=['statistics'])
async def get_user_categories_statistics(message: types.Message):
    """Выводит пользовательскую статистику расходов по категориям за месяц"""
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    first_day_current_month, first_day_next_month = get_months(current_date)
    user_categories_statistics = categories.get_user_categories_statistics(first_day_current_month, first_day_next_month)
    answer_text = 'Сатистика расходов по категориям за месяц: \n\n'

    for category, expenses in user_categories_statistics.items():
        answer_text += f"{category} - {expenses} руб.\n"

    await message.answer(answer_text)

@dp.message_handler(commands=['change'])
async def change_user_budget(message: types.Message):
    """Изменяет значения лимитированного бюджета пользователя"""
    user_id = message.from_user.id

    budget_values = message.text.split()[1:]
    if len(budget_values) == 1:
        day = budget_values[0]
        budget.change_user_budget(user_id, day_limit=int(day))
        await message.answer("Лимит на день изменен")
    elif len(budget_values) == 2:
        day, week = budget_values
        budget.change_user_budget(user_id, day_limit=int(day), week_limit=int(week))
        await message.answer("Лимит на день и неделю изменен")
    elif len(budget_values) == 3:
        day, week, month = budget_values
        budget.change_user_budget(user_id, day_limit=int(day), week_limit=int(week), month_limit=int(month))
        await message.answer("Лимит на день, неделю и месяц изменен")
    