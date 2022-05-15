import db_init


cursor = db_init.get_cursor()
connection = db_init.get_connection()

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