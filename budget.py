import db_init


cursor = db_init.get_cursor()
connection = db_init.get_connection()

def get_day_limit():
    """Возвращает лимит расходов на день

    Returns:
        str: лимит расходов на день
    """
    cursor.execute("""SELECT day_limit FROM budget WHERE name='base'""")
    return cursor.fetchone()[0]

def get_week_limit():
    """Возвращает лимит расходов на неделею

    Returns:
        str: лимит расходов на неделю
    """
    cursor.execute("""SELECT week_limit FROM budget WHERE name='base'""")
    return cursor.fetchone()[0]

def get_month_limit():
    """Возвращает лимит расходов на месяц

    Returns:
        str: лимит расходов на месяц
    """
    cursor.execute("""SELECT month_limit FROM budget WHERE name='base'""")
    return cursor.fetchone()[0]

def add_user_budget(user_id: int):
    """Добавляет пользователю значения лимитированного бюджета по умолчанию"""
    cursor.execute("""INSERT INTO budget(user_id, name, day_limit, week_limit, month_limit)
                    VALUES(?, 'base', 1000, 4000, 15000)""", (user_id, ))
    connection.commit()


def change_user_budget(user_id: int, day_limit:int=1000, week_limit:int=4000, month_limit:int=15000):
    """Изменяет значения лимитированного бюджета пользователя"""
    cursor.execute("""UPDATE budget SET day_limit=?, week_limit=?, month_limit=? WHERE user_id=?""", 
        (day_limit, week_limit, month_limit, user_id))
    connection.commit()