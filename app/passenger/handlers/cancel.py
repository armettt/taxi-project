from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text == "Скасувати замовлення")
async def cancel_order(message: Message):
    await message.answer("Активне замовлення скасовано")
