from loader import dp, bot
from aiogram import types
import db
import re


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
    """Приветствует пользователя и заносит его в БД"""
    user_id = message.from_user.id
    if not db.check_user_exists(user_id):
        db.add_new_user(user_id)
    await message.answer('Добро пожаловать')

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
        await message.answer("Неверно введена команда")
        return

    category = category_input if category_input in db.get_categories() else 'прочее' # определяем введенную пользователем категорию расхода
    
    db.add_expense(user_id, int(price), category)

    await message.answer(f"Внесен расход {price} руб. на {category}")