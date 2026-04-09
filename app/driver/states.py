from aiogram.fsm.state import StatesGroup, State


class RegisterDriver(StatesGroup):
    phone = State()
    brand = State()
    model = State()
    color = State()
    plate = State()
