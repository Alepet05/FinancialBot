import sqlite3 as sq


# подлючение к БД
connection = sq.connect('db.db')
cursor = connection.cursor()

def init_db():
    """Инициализирует БД"""
    create_users_table()
    create_categories_table()
    create_expenses_table()
    create_budget_table() 

def create_users_table():
    """Создает таблицу пользователей, если она отсутствует"""
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        join_date DATETIME DEFAULT (DATETIME('now', 'localtime'))
    )""")

def create_expenses_table():
    """Создает таблицу расходов, если она отсутствует"""
    cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        expense INTEGER,
        category TEXT,
        date DATE DEFAULT (DATE('now', 'localtime')),
        FOREIGN KEY (category) REFERENCES categories(category),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")

def create_categories_table():
    """Создает таблицу категорий расходов, если она отсутствует"""
    cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
        category TEXT UNIQUE,
        is_base_category BOOLEAN 
    )""")
    
    fill_categories_table()

def create_budget_table():
    """Создает таблицу бюджета, если она отсутствует"""
    cursor.execute("""CREATE TABLE IF NOT EXISTS budget (
        name TEXT,
        day_limit INTEGER DEFAULT 500,
        month_limit INTEGER DEFAULT 10000
    )""")

def fill_categories_table():
    """Заполняет таблицу категориями расходов"""
    categories = [
        ('такси', False),
        ('продукты', True),
        ('обед', True),
        ('кафе', False),
        ('транспорт', True),
        ('связь', True),
        ('интернет', True),
        ('прочее', False),
    ]
    cursor.executemany("INSERT INTO categories(category, is_base_category) VALUES(?, ?)", categories)
    connection.commit()

def change_budget(day_limit=500, month_limit=10000):
    """Изменяет значения лимитированного бюджета"""
    cursor.execute("""UPDATE budget SET day_limit=?, month_limit=?""", (day_limit, month_limit))
    connection.commit()

init_db()