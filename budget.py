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