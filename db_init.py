import sqlite3 as sq


# подлючение к БД
connection = sq.connect('db.db')
cursor = connection.cursor()

def get_cursor():
    return cursor

def get_connection():
    return connection
    
def init_db():
    """Инициализирует БД"""
    tables = {
        'users': create_users_table,
        'categories': create_categories_table,
        'expenses': create_expenses_table,
        'budget': create_budget_table
    }
    for table in tables:
        cursor.execute(f"""SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'""")
        name = cursor.fetchall()
        if name:
            continue
        tables[table]()

def create_users_table():
    """Создает таблицу пользователей, если она отсутствует"""
    cursor.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        join_date DATETIME DEFAULT (DATETIME('now', 'localtime'))
    )""")

def create_expenses_table():
    """Создает таблицу расходов, если она отсутствует"""
    cursor.execute("""CREATE TABLE expenses (
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
    cursor.execute("""CREATE TABLE categories (
        category TEXT UNIQUE,
        is_base_category BOOLEAN 
    )""")
    
    fill_categories_table()

def create_budget_table():
    """Создает таблицу бюджета, если она отсутствует"""
    cursor.execute("""CREATE TABLE budget (
        user_id INTEGER,
        name TEXT,
        day_limit INTEGER,
        week_limit INTEGER,
        month_limit INTEGER, 
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )""")

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

init_db()