from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

default_inclose = "inclose"


# Button to delete message and finish state
def get_inclose_kb(text: str, callback: str = default_inclose):
    b = InlineKeyboardMarkup()
    b.add(InlineKeyboardButton(text=text, callback_data=callback))
    return b


def get_inclose_button(text: str, callback: str = default_inclose):
    b = InlineKeyboardButton(text=text, callback_data=callback)
    return b
