import db_init


cursor = db_init.get_cursor()
connection = db_init.get_connection()

def get_all_categories():
    """Возвращает список всех категорий из бд

    Returns:
        list: список категорий
    """
    cursor.execute("""SELECT category FROM categories""")
    categories_names = cursor.fetchall()
    return [category[0] for category in categories_names] # преобразуем список кортежей в список названий категорий

def get_user_categories_statistics(current_month_date: str, next_month_date: str):
    """Возвращает статистику расходов пользователя за месяц

    Args:
        current_month_date (str): полная дата текущего месяца
        next_month_date (str): полная дата следующего месяца

    Returns:
        dict: словарь категорий и их расходов
    """

    all_categories = get_all_categories()
    user_categories_statistics = {}

    for category in all_categories:
        cursor.execute(F"""SELECT sum(price) AS sum FROM expenses 
                        JOIN users ON expenses.user_id = users.user_id
                        WHERE date >= '{current_month_date}' AND date < '{next_month_date}'
                        AND category=?""", (category, ))
        user_cat_expenses = cursor.fetchone()[0]
        if user_cat_expenses:
            user_categories_statistics[category] = user_cat_expenses
    return user_categories_statistics