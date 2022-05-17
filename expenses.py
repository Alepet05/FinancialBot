import db_init


cursor = db_init.get_cursor()
connection = db_init.get_connection()

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
    return last_expenses

def get_today_expenses(user_id: int, date: str):
    """Возвращает сумму расходов пользователя за сегодня

    Args:
        user_id (int):telegram-id пользователя
        date (str): текущая дата пользователя

    Returns:
        int: сумма расходов пользователя за сегодня
    """
    cursor.execute("""SELECT sum(price) as sum FROM expenses 
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE expenses.user_id=? AND date=?""", (user_id, date))
    today_expenses = cursor.fetchone()[0]
    return int(today_expenses) if today_expenses else 0

def get_today_base_expanses(user_id: int, date: str):
    """Возвращает сумму базовых расходов пользователя за сегодня

    Args:
        user_id (int):telegram-id пользователя
        date (str): текущая дата пользователя

    Returns:
        int: сумма базовых расходов пользователя за сегодня
    """
    cursor.execute("""SELECT sum(price) as sum FROM expenses 
                    JOIN categories ON expenses.category = categories.category
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE expenses.user_id=? AND date=? AND is_base_category=True""", (user_id, date))
    today_base_expanses = cursor.fetchone()[0]
    return int(today_base_expanses) if today_base_expanses else 0

def get_week_expenses(user_id: int, start_week: str, current_date: str):
    """Возвращает сумму расходов пользователя за текущую неделю

    Args:
        user_id (int): telegram-id пользователя
        start_week (str): начало текущей недели
        current_date (str): текущая дата

    Returns:
        int: сумма расходов пользователя за неделю
    """
    cursor.execute(f"""SELECT sum(price) as sum FROM expenses 
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE date >= '{start_week}' AND date <= '{current_date}'
                    AND expenses.user_id=?""", (user_id, ))

    month_expenses = cursor.fetchone()[0]
    return int(month_expenses) if month_expenses else 0

def get_week_base_expenses(user_id: int, start_week: str, current_date: str):
    """Возвращает сумму базовых расходов пользователя за текущую неделю

    Args:
        user_id (int): telegram-id пользователя
        start_week (str): начало текущей недели
        current_date (str): текущая дата

    Returns:
        int: сумма базовых расходов пользователя за неделю
    """
    cursor.execute(f"""SELECT sum(price) as sum FROM expenses 
                    JOIN categories ON expenses.category = categories.category
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE expenses.user_id=? AND is_base_category=True
                    AND date >= '{start_week}' AND date <= '{current_date}'""", (user_id, ))

    month_base_expenses = cursor.fetchone()[0]
    return int(month_base_expenses) if month_base_expenses else 0

def get_month_expenses(user_id: int, first_day_current_month: str, first_day_next_month: str):
    """Возвращает сумму расходов пользователя за текущий месяц

    Args:
        user_id (int): telegram-id пользователя
        first_day_current_month (str): дата первого дня текущего месяца
        first_day_next_month (str): дата первого дня следующего месяца

    Returns:
        int: сумма расходов пользователя за месяц. Если таковой нет - сообщение 
    """
    cursor.execute(f"""SELECT sum(price) as sum FROM expenses 
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE date >= '{first_day_current_month}' AND date < '{first_day_next_month}'
                    AND expenses.user_id=?""", (user_id, ))

    month_expenses = cursor.fetchone()[0]
    return int(month_expenses) if month_expenses else 0

def get_month_base_expenses(user_id: int, first_day_current_month: str, first_day_next_month: str):
    """Возвращает сумму базовых расходов пользователя за текущий месяц

    Args:
        user_id (int): telegram-id пользователя
        first_day_current_month (str): дата первого дня текущего месяца
        first_day_next_month (str): дата первого дня следующего месяца

    Returns:
        int: сумма базовых расходов пользователя за месяц
    """
    cursor.execute(f"""SELECT sum(price) as sum FROM expenses 
                    JOIN categories ON expenses.category = categories.category
                    JOIN users ON expenses.user_id = users.user_id
                    WHERE expenses.user_id=? AND is_base_category=True
                    AND date >= '{first_day_current_month}' AND date < '{first_day_next_month}'""", (user_id, ))

    month_base_expenses = cursor.fetchone()[0]
    return int(month_base_expenses) if month_base_expenses else 0