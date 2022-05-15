import db_init


cursor = db_init.get_cursor()
connection = db_init.get_connection()

def get_categories():
    """Возвращает список категорий из бд

    Returns:
        list: список категорий
    """
    cursor.execute("""SELECT category FROM categories""")
    categories_names = cursor.fetchall()
    return [category[0] for category in categories_names] # преобразуем список кортежей в список названий категорий