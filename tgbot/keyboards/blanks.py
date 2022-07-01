from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Button to delete message and finish state 
def inclose(text: str, callback: str = 'inclose'):
    b = InlineKeyboardMarkup()
    b.add(InlineKeyboardButton(text=text, callback_data=callback))
    return b

