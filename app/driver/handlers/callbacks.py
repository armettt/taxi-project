from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.core.database import pool
from app.core.config import GROUP_ID_PASSENGER
import time

router = Router()
CALLBACK_COOLDOWN = {}


def take_order_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📍 Прибув",
                callback_data=f"arrived_{order_id}"
            )]
        ]
    )


def complete_order_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Завершити поїздку",
                callback_data=f"complete_{order_id}"
            )]
        ]
    )


@router.callback_query(F.data.startswith("take_"))
async def take_order(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    order_id = int(callback.data.split("_")[1])
    now = time.time()

    # Антиспам
    if user_id in CALLBACK_COOLDOWN and now - CALLBACK_COOLDOWN[user_id] < 2:
        await callback.answer("Зачекай...")
        return
    CALLBACK_COOLDOWN[user_id] = now

    async with pool.acquire() as conn:
        driver = await conn.fetchrow(
            "SELECT * FROM drivers WHERE user_id=$1", user_id
        )

        if not driver:
            await callback.answer(
                "❌ Ви не зареєстровані як водій",
                show_alert=True
            )
            return

        order = await conn.fetchrow(
            "SELECT * FROM orders WHERE id=$1", order_id
        )

        if not order:
            await callback.answer("Замовлення не знайдено")
            return

        if order["status"] != "waiting":
            await callback.answer("Замовлення вже взято")
            return

        await conn.execute(
            "UPDATE orders SET status='taken', driver_id=$1 WHERE id=$2",
            user_id, order_id
        )

    driver_info = (
        f"🚖 <b>Водій:</b>\n"
        f"👤 @{driver['username']}\n"
        f"📞 {driver['phone']}\n"
        f"🚗 {driver['brand']} {driver['model']}\n"
        f"🎨 {driver['color']}\n"
        f"🔢 {driver['plate']}"
    )

    text = (
        f"🚕 <b>Замовлення #{order_id}</b>\n\n"
        f"📞 Телефон: {order['phone']}\n"
        f"👤 Клієнт: {order['username']}\n"
        f"📍 Маршрут: {order['from_loc']} → {order['to_loc']}\n"
        f"💬 Коментар: {order['comment']}\n\n"
        f"✅ <b>Замовлення прийнято</b>\n\n"
        f"{driver_info}"
    )

    await bot.edit_message_text(
        text=text,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        parse_mode="HTML",
        reply_markup=take_order_kb(order_id)
    )

    await bot.send_message(
        order["client_id"],
        f"🚖 Ваше замовлення прийнято!\n\n{driver_info}",
        parse_mode="HTML"
    )

    await callback.answer("Ви взяли замовлення")


@router.callback_query(F.data.startswith("arrived_"))
async def arrived_order(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    order_id = int(callback.data.split("_")[1])

    async with pool.acquire() as conn:
        order = await conn.fetchrow(
            "SELECT * FROM orders WHERE id=$1", order_id
        )

        if not order:
            await callback.answer("Замовлення не знайдено")
            return

        if order["driver_id"] != user_id:
            await callback.answer(
                "❌ Це не ваше замовлення",
                show_alert=True
            )
            return

        await conn.execute(
            "UPDATE orders SET status='arrived' WHERE id=$1",
            order_id
        )

    text = (
        f"🚕 <b>Замовлення #{order_id}</b>\n\n"
        f"👤 Клієнт: {order['username']}\n"
        f"📍 Маршрут: {order['from_loc']} → {order['to_loc']}\n"
        f"💬 Коментар: {order['comment']}\n\n"
        f"📍 <b>Водій прибув</b>"
    )

    await bot.edit_message_text(
        text=text,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        parse_mode="HTML",
        reply_markup=complete_order_kb(order_id)
    )

    await bot.send_message(
        order["client_id"],
        f"🚖 Водій прибув! Замовлення №{order_id}"
    )

    await callback.answer("Ви прибули")


@router.callback_query(F.data.startswith("complete_"))
async def complete_order(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    order_id = int(callback.data.split("_")[1])

    async with pool.acquire() as conn:
        order = await conn.fetchrow(
            "SELECT * FROM orders WHERE id=$1", order_id
        )

        if not order:
            await callback.answer("Замовлення не знайдено")
            return

        if order["driver_id"] != user_id:
            await callback.answer(
                "❌ Це не ваше замовлення",
                show_alert=True
            )
            return

        await conn.execute(
            "UPDATE orders SET status='completed' WHERE id=$1",
            order_id
        )

    text = (
        f"🚕 <b>Замовлення #{order_id}</b>\n\n"
        f"👤 Клієнт: {order['username']}\n"
        f"📍 Маршрут: {order['from_loc']} → {order['to_loc']}\n"
        f"💬 Коментар: {order['comment']}\n\n"
        f"✅ <b>Поїздку завершено</b>"
    )

    await bot.edit_message_text(
        text=text,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        parse_mode="HTML"
    )

    await bot.send_message(
        order["client_id"],
        f"✅ Поїздка №{order_id} завершена. Дякуємо!"
    )

    await callback.answer("Поїздку завершено")
