from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


from keyboards.keyboard import catalog_button

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Выберите раздел:", reply_markup=catalog_button())

