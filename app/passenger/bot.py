from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.core.config import BOT_TOKEN_PASSENGER
from app.passenger.handlers import start, order, cancel


def create_passenger_bot():
    bot = Bot(token=BOT_TOKEN_PASSENGER, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(order.router)
    dp.include_router(cancel.router)

    return bot, dp
