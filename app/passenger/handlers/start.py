from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

router = Router()


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Створити замовлення")],
            [KeyboardButton(text="Скасувати замовлення")]
        ],
        resize_keyboard=True
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Використовуй кнопки нижче",
        reply_markup=main_menu()
    )
