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
    kb.add(InlineKeyboardButton(text='Найти пользователя', callback_data='adm-action_find-user'))
    return kb

def get_user_moderate_keyboard(user_id: str):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Отправить сообщение', callback_data=f'adm-user_send-message_{user_id}'))
    kb.add(InlineKeyboardButton(text='Блокировка', callback_data=f'adm-user_ban_{user_id}'))
    kb.add(InlineKeyboardButton(text='Редактировать', callback_data=f'adm-user_edit_{user_id}'))
    return kb
