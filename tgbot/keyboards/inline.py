from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_admin_panel_keyboard(buttons_list: str = None, *buttons):
    kb = InlineKeyboardMarkup()
    if not buttons_list:
        for button in buttons:
            kb.add(button)
    else:
        for button in buttons_list:
            kb.add(button)
    return kb

def get_stats_panel_keyboard():
    kb = InlineKeyboardMarkup()
    #TODO: kb.add(...)
    return kb

def get_users_panel_keyboard():
    kb = InlineKeyboardMarkup()
    #TODO: kb.add(...)
    return kb

