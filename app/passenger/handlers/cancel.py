from aiogram import Router, F, Bot
from aiogram.types import Message
from app.core.database import pool
from app.core.config import GROUP_ID_PASSENGER

router = Router()


@router.message(F.text == "Скасувати замовлення")
async def cancel_order(message: Message, bot: Bot):
    user_id = message.from_user.id

    async with pool.acquire() as conn:
        order = await conn.fetchrow("""
            SELECT id, message_id
            FROM orders
            WHERE client_id=$1 AND status='waiting'
            ORDER BY id DESC LIMIT 1
        """, user_id)

        if not order:
            await message.answer("Немає активного замовлення")
            return

        await conn.execute(
            "DELETE FROM orders WHERE id=$1",
            order["id"]
        )

    try:
        await bot.edit_message_text(
            "❌ Замовлення скасовано клієнтом",
            chat_id=GROUP_ID_PASSENGER,
            message_id=order["message_id"]
        )
    except:
        pass

    await message.answer("Замовлення скасовано")
