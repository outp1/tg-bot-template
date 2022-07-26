from aiogram.dispatcher.filters.state import State, StatesGroup

class AdminStates(StatesGroup):
    find_user = State()
