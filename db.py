from datetime import datetime
import sqlite3 as sq


# подлючение к БД
connection = sq.connect('db.db')
cursor = connection.cursor()

def add_new_user(user_id: int):
    """Добавляет нового пользователя в БД

    Args:
        user_id (int): telegram-id пользователя
    """
    cursor.execute("""INSERT INTO users (user_id) VALUES (?)""", (user_id, ))
    connection.commit()

def check_user_exists(user_id):
    """Проверяет, существует ли пользователь с переданным id в БД

    Args:
        user_id (int): telegram-id пользователя

    Returns:
        [tuple, None]: Объект cursor, если пользователь был найден, иначе - None
    """
    user = cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id, ))
    return user.fetchone()

def add_expense(user_id: int, price: int, category: str):
    """Добавляет расход в БД

    Args:
        user_id (int): telegram-id пользователя
        price (int): стоимость расхода
        category (str): категория расхода
    """
    cursor.execute("""INSERT INTO expenses (user_id, price, category) VALUES (?, ?, ?)""", 
        (user_id, price, category))
    connection.commit()

def get_last_expenses(user_id: int, expenses_count: int):
    """Выводит последние expenses_count расходов

    Args:
        user_id (int): telegram-id пользователя
        expenses_count (int): кол-во последних расходов для вывода

    Returns:
        [list, str]: список последних расходов. Если таковых нет - сообщение об отсутствии расходов
    """
    cursor.execute("""SELECT category, price, date FROM expenses
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE expenses.user_id=? LIMIT ?""", (user_id, expenses_count))
    last_expenses = cursor.fetchall()
    return last_expenses if last_expenses else 'Отсутствуют какие-либо расходы'

def get_categories():
    """Возвращает список категорий из бд

    Returns:
        list: список категорий
    """
    cursor.execute("""SELECT category FROM categories""")
    categories_names = cursor.fetchall()
    return [category[0] for category in categories_names] # преобразуем список кортежей в список названий категорий

def get_today_expenses(user_id: int, date: str):
    """Возвращает сумму расходов пользователя за сегодня

    Args:
        user_id (int):telegram-id пользователя
        date (str): текущая дата пользователя

    Returns:
        str: сумма расходов пользователя за сегодня. Если таковой нет - сообщение об отсутствии расходов
    """
    cursor.execute("""SELECT sum(price) as sum FROM expenses 
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE expenses.user_id=? AND date=?""", (user_id, date))
    today_expenses = cursor.fetchone()[0]
    return today_expenses if today_expenses else 'За сегодня еще нет расходов'

def get_today_base_expanses(user_id: int, date: str):
    """Возвращает сумму базовых расходов пользователя за сегодня

    Args:
        user_id (int):telegram-id пользователя
        date (str): текущая дата пользователя

    Returns:
        [str, None]: сумма базовых расходов пользователя за сегодня. Если таковой нет - сообщение об отсутствии расходов
    """
    cursor.execute("""SELECT sum(price) as sum FROM expenses 
                    JOIN categories ON expenses.category = categories.category
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE expenses.user_id=? AND date=? AND is_base_category=True""", (user_id, date))
    today_base_expanses = cursor.fetchone()[0]
    return today_base_expanses if today_base_expanses else 'За сегодня еще нет базовых расходов'

def get_day_limit():
    """Возвращает лимит расходов на день

    Returns:
        str: лимит расходов на день
    """
    cursor.execute("""SELECT day_limit FROM budget WHERE name='base'""")
    return cursor.fetchone()[0]

def get_month_expenses(user_id: int, current_month: str, next_month: str):
    """Возвращает сумму расходов пользователя за текущий месяц

    Args:
        user_id (int): telegram-id пользователя
        current_month (str): текущий месяц
        next_month (str): следующий месяц

    Returns:
        str: сумма расходов пользователя за месяц. Если таковой нет - сообщение 
    """
    cursor.execute(f"""SELECT sum(price) as sum FROM expenses 
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE date >= '{current_month}' AND date < '{next_month}'
                    AND expenses.user_id=?""", (user_id, ))

    month_expenses = cursor.fetchone()[0]
    return month_expenses if month_expenses else 'За текущий месяц еще нет расходов'

def get_month_base_expenses(user_id: int, current_month: str, next_month: str):
    """Возвращает сумму базовых расходов пользователя за текущий месяц

    Args:
        user_id (int): telegram-id пользователя
        current_month (str): текущий месяц
        next_month (str): следующий месяц

    Returns:
        str: сумма базовых расходов пользователя за месяц. Если таковой нет - сообщение 
    """
    cursor.execute(f"""SELECT sum(price) as sum FROM expenses 
                    JOIN categories ON expenses.category = categories.category
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE expenses.user_id=? AND is_base_category=True
                    AND date >= '{current_month}' AND date < '{next_month}'""", (user_id, ))

    month_base_expenses = cursor.fetchone()[0]
    return month_base_expenses if month_base_expenses else 'За текущий месяц еще нет базовых расходов'

def get_month_limit():
    """Возвращает лимит расходов на месяц

    Returns:
        str: лимит расходов на месяц
    """
    cursor.execute("""SELECT month_limit FROM budget WHERE name='base'""")
    return cursor.fetchone()[0]

def init_db():
    """Инициализирует БД"""
    create_users_table()
    create_categories_table()
    create_expenses_table()
    create_budget_table() 

def create_users_table():
    """Создает таблицу пользователей, если она отсутствует"""
    cursor.execute("""DROP TABLE IF EXISTS users""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        join_date DATETIME DEFAULT (DATETIME('now', 'localtime'))
    )""")

def create_expenses_table():
    """Создает таблицу расходов, если она отсутствует"""
    cursor.execute("""DROP TABLE IF EXISTS expenses""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        price INTEGER,
        category TEXT,
        date DATE DEFAULT (DATE('now', 'localtime')),
        FOREIGN KEY (category) REFERENCES categories(category),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")

def create_categories_table():
    """Создает таблицу категорий расходов, если она отсутствует"""
    cursor.execute("""DROP TABLE IF EXISTS categories""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
        category TEXT UNIQUE,
        is_base_category BOOLEAN 
    )""")
    
    fill_categories_table()

def create_budget_table():
    """Создает таблицу бюджета, если она отсутствует"""
    cursor.execute("""DROP TABLE IF EXISTS budget""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS budget (
        name TEXT,
        day_limit INTEGER DEFAULT 500,
        month_limit INTEGER DEFAULT 10000
    )""")
    fill_budget_table(name='base', day_limit=500, month_limit=10000)

def fill_categories_table():
    """Заполняет таблицу категориями расходов"""
    categories = [
        ('такси', True),
        ('продукты', True),
        ('обед', True),
        ('кафе', True),
        ('транспорт', False),
        ('интернет и связь', False),
        ('фастфуд', True),
        ('коммунальные услуги', False),
        ('товары', True),
        ('подписки', False),
        ('дом', True),
        ('развлечения', True),
        ('медицина', False),
        ('личное', True),
        ('прочее', True),
    ]
    cursor.executemany("INSERT INTO categories(category, is_base_category) VALUES(?, ?)", categories)
    connection.commit()
    
def fill_budget_table(name: str, day_limit: int, month_limit: int):
    """Заполняет таблицу бюджета

    Args:
        name (str): название бюджета (базовый или нет)
        day_limit (int): лимит расходов на день
        month_limit (int): лимит расходов на месяц
    """
    cursor.execute("INSERT INTO budget(name, day_limit, month_limit) VALUES(?, ?, ?)",
        (name, day_limit, month_limit))
    connection.commit()

def change_budget(day_limit=1000, month_limit=15000):
    """Изменяет значения лимитированного бюджета"""
    cursor.execute("""UPDATE budget SET day_limit=?, month_limit=?""", (day_limit, month_limit))
    connection.commit()

init_db()