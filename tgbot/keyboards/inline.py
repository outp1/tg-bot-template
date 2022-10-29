from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class AdminPanelKeyboards:

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
    
    def get_advert_panel_keyboard():
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text='Полный список', callback_data='advertpanel_full'))
        kb.add(InlineKeyboardButton(text='Редактировать', callback_data='advertpanel_edit'))
        return kb
    
    def get_advert_edit_keybord(advert_id, close_callbackdata = 'inclose'):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text='Изменить текст', callback_data=f'advertedit_text_{advert_id}'))
        kb.add(InlineKeyboardButton(text='Добавить/изменить медиа', callback_data=f'advertedit_media_{advert_id}'))
        kb.add(InlineKeyboardButton(text='Добавить/изменить кнопки', callback_data=f'advertedit_kbs_{advert_id}'))
        kb.add(InlineKeyboardButton(text='Изменить дату отправки', callback_data=f'advertedit_data_{advert_id}'))
        kb.add(InlineKeyboardButton(text='Отправить сейчас', callback_data=f'advertedit_send_{advert_id}'))
        kb.add(InlineKeyboardButton(text='Удалить объявление', callback_data=f'advertedit_remove_{advert_id}'))
        kb.add(InlineKeyboardButton(text='❌', callback_data=close_callbackdata))
        return kb
    
    def get_advertfull_keyboard():
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text='Редактировать', callback_data='advertpanel_edit'))
        return kb
    
    def get_kb_type_choosing():
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text='Ссылка', callback_data='kbtypechoosing-url'))
        kb.add(InlineKeyboardButton(text='Всплывающее окно', callback_data='kbtypechoosing-popup_message'))
        kb.add(InlineKeyboardButton(text='Коллбек боту', callback_data='kbtypechoosing-callback_data'))
        return kb
    
    #TODO:
    def return_kb(advert_id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text='🔙', callback_data=f'goreturn-advert_{advert_id}'))
        return kb
