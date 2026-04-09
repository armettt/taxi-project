from aiogram import Router, F, Bot
from aiogram.types import (
    Message, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from app.passenger.states import OrderState
from app.core.database import pool
from app.core.config import GROUP_ID_PASSENGER
import time

router = Router()
user_last_order_time = {}
user_active_order = {}


def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(
            text="Надіслати номер", request_contact=True)]],
        resize_keyboard=True
    )


def take_order_button(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚖 Взяти замовлення",
                callback_data=f"take_{order_id}"
            )]
        ]
    )


@router.message(F.text == "Створити замовлення")
async def start_order(message: Message, state: FSMContext):
    await message.answer("Надішли номер телефону", reply_markup=contact_kb())
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
    user_id = message.from_user.id
    now = time.time()

    if user_id in user_last_order_time and now - user_last_order_time[user_id] < 30:
        await message.answer("Зачекайте 30 секунд перед новим замовленням")
        return

    if user_active_order.get(user_id):
        await message.answer("У вас вже є активне замовлення")
        return

    data = await state.get_data()
    username = message.from_user.username or message.from_user.first_name

    async with pool.acquire() as conn:
        order_id = await conn.fetchval("""
            INSERT INTO orders
            (client_id, phone, username, from_loc, to_loc, comment, status)
            VALUES ($1,$2,$3,$4,$5,$6,'waiting')
            RETURNING id
        """, user_id, data["phone"], username,
             data["from_loc"], data["to_loc"], message.text)

    text = (
        f"🚕 <b>Замовлення #{order_id}</b>\n\n"
        f"📞 {data['phone']}\n"
        f"👤 {username}\n"
        f"📍 {data['from_loc']} → {data['to_loc']}\n"
        f"💬 {message.text}"
    )

    sent = await bot.send_message(
        GROUP_ID_PASSENGER,
        text,
        parse_mode="HTML",
        reply_markup=take_order_button(order_id)
    )

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE orders SET message_id=$1 WHERE id=$2",
            sent.message_id, order_id
        )

    user_last_order_time[user_id] = now
    user_active_order[user_id] = order_id

    await message.answer("✅ Замовлення створено")
    await state.clear()
