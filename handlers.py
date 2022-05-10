from loader import dp
from aiogram import types


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message):
    await message.answer('Добро пожаловать')