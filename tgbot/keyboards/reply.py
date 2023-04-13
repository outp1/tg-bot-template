from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(text="Профиль"))
    return kb
