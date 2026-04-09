from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from app.driver.states import RegisterDriver
from app.core.database import pool

router = Router()


def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(
            text="📱 Отправить номер", request_contact=True)]],
        resize_keyboard=True
    )


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Отправьте номер телефона",
        reply_markup=phone_kb()
    )


@router.message(RegisterDriver.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Марка авто:")
    await state.set_state(RegisterDriver.brand)


@router.message(F.contact)
async def start_registration(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Марка авто:")
    await state.set_state(RegisterDriver.brand)


@router.message(RegisterDriver.brand)
async def get_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await state.set_state(RegisterDriver.model)
    await message.answer("Модель авто:")


@router.message(RegisterDriver.model)
async def get_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(RegisterDriver.color)
    await message.answer("Цвет авто:")


@router.message(RegisterDriver.color)
async def get_color(message: Message, state: FSMContext):
    await state.update_data(color=message.text)
    await state.set_state(RegisterDriver.plate)
    await message.answer("Номер авто:")


@router.message(RegisterDriver.plate)
async def save_driver(message: Message, state: FSMContext):
    data = await state.get_data()

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO drivers
            (user_id, username, phone, brand, model, color, plate)
            VALUES ($1,$2,$3,$4,$5,$6,$7)
            ON CONFLICT (user_id) DO UPDATE SET
            username=$2, phone=$3, brand=$4,
            model=$5, color=$6, plate=$7
        """,
            message.from_user.id,
            message.from_user.username,
            data["phone"],
            data["brand"],
            data["model"],
            data["color"],
            message.text
        )

    await message.answer("Регистрация завершена!")
    await state.clear()
