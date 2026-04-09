from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from app.passenger.states import OrderState
from app.core.database import pool
from app.core.config import GROUP_ID_PASSENGER
from aiogram import Bot

router = Router()
user_active_order = {}


@router.message(F.text == "Створити замовлення")
async def create_order_start(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(
            text="Надіслати номер", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer("Надішли номер телефону", reply_markup=kb)
    await state.set_state(OrderState.phone)


@router.message(OrderState.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await message.answer("Звідки їхати?")
    await state.set_state(OrderState.from_loc)


@router.message(OrderState.from_loc)
async def get_from(message: Message, state: FSMContext):
    await state.update_data(from_loc=message.text)
    await message.answer("Куди їхати?")
    await state.set_state(OrderState.to_loc)


@router.message(OrderState.to_loc)
async def get_to(message: Message, state: FSMContext):
    await state.update_data(to_loc=message.text)
    await message.answer("Коментар або '-'")
    await state.set_state(OrderState.comment)


@router.message(OrderState.comment)
async def finish_order(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    async with pool.acquire() as conn:
        order_id = await conn.fetchval("""
            INSERT INTO orders
            (client_id, phone, username, from_loc, to_loc, comment)
            VALUES ($1,$2,$3,$4,$5,$6)
            RETURNING id
        """, user_id, data["phone"], username,
             data["from_loc"], data["to_loc"], message.text)

    text = (
        f"🚕 Замовлення #{order_id}\n"
        f"📞 {data['phone']}\n"
        f"📍 {data['from_loc']} → {data['to_loc']}\n"
        f"💬 {message.text}"
    )

    await bot.send_message(GROUP_ID_PASSENGER, text)
    await message.answer("Замовлення створено")
    await state.clear()
