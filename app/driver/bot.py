from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.core.config import BOT_TOKEN_DRIVER
from app.driver.handlers import register, callbacks


def create_driver_bot():
    bot = Bot(token=BOT_TOKEN_DRIVER, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(register.router)
    dp.include_router(callbacks.router)

    return bot, dp
