from aiogram.fsm.state import StatesGroup, State


class OrderState(StatesGroup):
    phone = State()
    from_loc = State()
    to_loc = State()
    comment = State()
