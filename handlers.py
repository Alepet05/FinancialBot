from loader import dp, bot
from aiogram import types
import db


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
    user_id = message.from_user.id
    if not db.check_user_exists(user_id):
        db.add_new_user(user_id)
    await message.answer('Добро пожаловать')