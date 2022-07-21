from aiogram.types import InlineKeyboardButton

admin_panel_buttons = [
        InlineKeyboardButton(text='Статистика', callback_data='adm-panel_stats'),
        InlineKeyboardButton(text='Пользователи', callback_data='adm-panel_users')
        ]
