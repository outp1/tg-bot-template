import logging
from typing import Union
import json
import traceback
import datetime

from aiogram import Dispatcher, Bot, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BadRequest
import pytz

from tgbot.models import (UserTables, ContentTables, 
        ModeratingHistoryTables, AdvertisingTables)
from tgbot import keyboards
from tgbot.keyboards import AdminPanelKeyboards
from tgbot.misc.states import AdminStates
from tgbot.misc.tools import safe_list_get, generate_id_async
from .deep_logic import admin_panel

#TODO: CODE REFACTORING. EMERGENCY.

async def admin_panel_start(message: types.Message, logger, bot: Bot, state: FSMContext):
    try: 
        await state.finish()
    except:
        pass
    kbs = AdminPanelKeyboards.get_admin_panel_keyboard(bot["config"].tg_bot.admin_panel_buttons)
    kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
    await message.answer("Hello, admin!", reply_markup=kbs)


# Admin panel start buttons
async def admin_panel_actions(call: types.CallbackQuery, state: FSMContext, 
        bot: Bot, logger: logging.Logger, user_tables: UserTables, advertising_tables: AdvertisingTables):
    try:
        await state.finish()
    except:
        pass
    action = call.data.split('_')[1]
    if action == 'stats':    
        content = await admin_panel.take_stats_content(user_tables, logger)
        kbs = AdminPanelKeyboards.get_stats_panel_keyboard()
        kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
        await call.message.answer(content, reply_markup=kbs)
    elif action == 'users':
        content = await admin_panel.take_users_content(user_tables, logger)
        kbs = AdminPanelKeyboards.get_users_panel_keyboard()
        kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
        await call.message.answer(content, reply_markup=kbs)
    elif action == 'advertisements': 
        content = await admin_panel.take_advert_content(advertising_tables, logger)
        kbs = AdminPanelKeyboards.get_advert_panel_keyboard()
        kbs.add(keyboards.inclose_button(text=bot["config"].misc.inclose_text))
        await call.message.answer(content, reply_markup=kbs)


# All admin panel actions buttons
async def admin_actions(call: types.CallbackQuery, state: FSMContext, 
        bot: Bot, logger: logging.Logger, user_tables: UserTables):
    data = call.data.split('_')
    action = data[1]
    if action == 'find-user':
        kb = keyboards.inclose(bot["config"].misc.inclose_text)
        msg = await call.message.answer('<b>Введите циферный айди или никнейм юзера через @:</b>', reply_markup=kb)
        await state.update_data(msg=msg)
        await AdminStates.find_user.set()        
    elif action == 'export-stat':
        pass


# find-user action
async def find_user_state(message: types.Message, state: FSMContext, 
        bot: Bot, logger: logging.Logger, user_tables: UserTables):
    data = await state.get_data()
    try: 
        await bot.delete_message(message.from_user.id, data["message"].message_id)
    except:
        pass
    content = await admin_panel.take_find_user_content(message, user_tables, state, bot, logger)
    if not content:
        return await message.answer('<b>Данные введены неверно. Попробуйте ещё раз:</b>', 
                reply_markup=keyboards.inclose(bot["config"].misc.inclose_text))
    else:
        kb = AdminPanelKeyboards.get_user_moderate_keyboard(message.text)
        kb.add(keyboards.inclose_button(bot["config"].misc.inclose_text))
        await message.answer(content, reply_markup=kb)


# users managing actions 
async def admin_user_actions(call: types.CallbackQuery, bot: Bot, 
        logger: logging.Logger, user_tables: UserTables):
    data = call.data.split('_')
    action, user = data[1], data[2] 
    if action == 'ban':
        await call.message.answer(f'<i>Введите:</i>\n\n' +
                f'<b>Временный бан -</b> <code>!ban {user} количество время</code> (примеры времени: 5 d, 12 h, 5 m)\n\n' +
                f'<b>Перманентный бан -</b> <code>!ban {user}</code>\n\n' +
                f'<b>Снять любую блокировку</b> - <code>!unban {user}</code>\n\n',
                reply_markup=keyboards.inclose(bot['config'].misc.inclose_text))       
    elif action == 'edit': await call.message.answer(f'<i>Введите:</i>\n\n' +
                f'<b>Редактирование пользователя -</b> <code>!edit_user {user} название_ячейки_данных новое_значение</code>\n\n' +
                f'<b>Пример - </b> <code>!edit_user {user} reg_date 2022.08.30</code>\n\n',
                reply_markup=keyboards.inclose(bot['config'].misc.inclose_text))       
    elif action == 'send-message': 
        await call.message.answer(f'<i>Введите:</i>\n\n' +
                f'<b>Отправка сообщения -</b> <code>!adm_send_message {user} сообщение</code>\n\n' +
                f'<b>Пример - </b> <code>!adm_send_message {user} Привет, смертный</code>\n\n',
                reply_markup=keyboards.inclose(bot['config'].misc.inclose_text))       

# advertising functions
async def admin_advertpanel(call: types.CallbackQuery, advertising_tables: AdvertisingTables, 
        logger: logging.Logger, bot: Bot, state: FSMContext):
    action = call.data.split('_')[1]
    if action == 'full':
        text = await admin_panel.get_content_advertpanel_full(call, advertising_tables, logger)
        kb = AdminPanelKeyboards.get_advertfull_keyboard()
        kb.add(keyboards.inclose_button(text=bot['config'].misc.inclose_text))
        await call.message.answer(text, reply_markup=kb)
    elif action == 'edit':
        kb = keyboards.inclose(bot["config"].misc.inclose_text)
        msg = await call.message.answer('Введите айди объявления для редактирования: ', reply_markup=kb)
        await state.update_data(msg=msg)
        await AdminStates.find_advert.set()

async def send_advert_to_user(advert, user_id, bot: Bot):
    if advert['inline_buts']:
        if type(advert['inline_buts']) is dict:
            kb = types.InlineKeyboardMarkup()
            _type_value = {advert['inline_buts']['_type']: advert['inline_buts']['content']}
            kb.add(types.InlineKeyboardButton(text=advert['text'], **_type_value))
        else:
            kb = types.InlineKeyboardMarkup()
            for b in advert['inline_buts']:
                _type_value = {b['_type']: b['content']}
                kb.add(types.InlineKeyboardButton(text=b['text'], **_type_value))
    else:
        kb = types.InlineKeyboardMarkup()
    if advert['media_type'] == 'media_group':
        medias = []
        for obj in advert['media']:
            medias.append(obj)
        medias[0]['caption'] = advert['text'] 
        media_group = types.MediaGroup()
        media_group.attach_many(*medias)
        msg = await bot.send_media_group(chat_id=user_id, media=media_group)
    elif advert['media_type'] == 'photo':
        msg = await bot.send_photo(chat_id=user_id, photo=advert['media'], caption=advert['text'], reply_markup=kb)
    elif advert['media_type'] == 'video':
        msg = await bot.send_video(chat_id=user_id, video=advert['media'], caption=advert['text'], reply_markup=kb)
    elif advert['media_type'] == 'document':
        msg = await bot.send_document(chat_id=user_id, document=advert['document'], caption=advert['text'], reply_markup=kb)
    else: 
        msg = await bot.send_message(chat_id=user_id, text=advert['text'], reply_markup=kb)
    return msg

async def send_advert_preview(advert, reply_markup, advertising_tables: AdvertisingTables, bot: Bot, 
        message: types.Message = None, call: types.CallbackQuery = None, 
        logger: logging.Logger = logging):
    if advert['sending_date'] is None:
        sending_date = 'Не установлено'
    else:
        sending_date = datetime.datetime.strftime(advert['sending_date'], '%H:%M %Y.%m.%d')
    if advert['sending_status'] == True:
        status = 'Отправлено'
    else:
        status = 'Не отправлено'
    text = f"""
<b>{advert['advert_header']}</b>

ID рекламы: <code>{advert['advert_id']}</code> 

Дата отправки: <code>{sending_date}</code>
Статус отправки:: <code>{status}</code>

<b>Выберите действие:</b>
"""
    if message:
        msg1 = await message.answer('Предпросмотр:')
        try:
            msg2 = await send_advert_to_user(advert, message.from_user.id, bot)
        except BadRequest:
            logger.info('ERROR ->')
            logger.info(traceback.format_exc())
            logger.info('START REMOVING BROKE KEYBOARD')
            await advertising_tables.update_advertising(advert['advert_id'], 'inline_buts', None)
            return await message.answer('Ошибка клавиатуры, удаление. Попробуйте ещё раз.')
        msg3 = await message.answer(text, reply_markup=reply_markup)
        return [msg1, msg2, msg3]

async def advert_message_edit_menu(advertising_tables: AdvertisingTables, 
        logger: logging.Logger, state: FSMContext, bot: Bot,
        message: types.Message = None, call: types.CallbackQuery = None, advert_id = None):
    data = await state.get_data()
    try:
        await state.finish()
    except:
        pass
    if message:
        if advert_id:
            kbs = AdminPanelKeyboards.get_advert_edit_keybord(advert_id, 'multiInclose_with_state')
            advert = await advertising_tables.get_advertising('advert_id', advert_id)
            msgs = await send_advert_preview(advert, kbs, advertising_tables, bot, message=message, logger=logger)  
            await state.update_data(msgs=msgs)
        elif data: 
            kbs = AdminPanelKeyboards.get_advert_edit_keybord(data['advert_id'], 'multiInclose_with_state')
            msg1 = await message.answer('<b>Предпросмотр:</b>')
            msg2 = await message.answer(data['text'])
            msg3 = await message.answer('Выберите действие', reply_markup=kbs)
            await state.update_data(msgs=[msg1, msg2, msg3])
        else:
            raise BaseException('Have no advertising id or state data for the function to work')
    else:
        raise BaseException('neither Message nor Call was transmitted') #TODO: refactor exceptions to external classes

async def advert_edit_actions(call: types.CallbackQuery, advertising_tables: AdvertisingTables, 
        logger: logging.Logger, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    try:
        for msg in state_data['msgs']:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=msg.message_id)
    except:
        pass
    data = call.data.split('_')
    action, advert_id = data[1], data[2]
    #TODO: Other media types support
    if action == 'media':
        msg = await call.message.answer('Отправьте медиа одним сообщением: ', reply_markup=AdminPanelKeyboards.back_to_advert_kb(data[2]))
        await state.update_data(advert_id=advert_id, msg=msg)
        await AdminStates.advert_media.set() 
    elif action == 'text':
        msg = await call.message.answer('Отправьте новый текст для объявления', reply_markup=AdminPanelKeyboards.back_to_advert_kb(data[2]))
        await state.update_data(advert_id=advert_id, msg=msg)
        await AdminStates.advert_text.set()
    elif action == 'remove':
        kb = types.InlineKeyboardMarkup() 
        kb.add(types.InlineKeyboardButton(text='Подтверждаю', callback_data=f'confirmadremove_{advert_id}'))
        kb.add(types.InlineKeyboardButton(text='Отмена', callback_data=f'advert-return_{advert_id}'))
        await call.message.answer(f'Вы уверены что хотите удалить объявление <code>{advert_id}</code>', reply_markup=kb)
    elif action == 'kbs':
        advert = await advertising_tables.get_advertising('advert_id', advert_id)
        inline_buts = advert['inline_buts']
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Очистить и добавить', callback_data=f'advert-kb_clean-add_{advert_id}'), 
                    types.InlineKeyboardButton(text='Добавить', callback_data=f'advert-kb_add_{advert_id}'))
        kb.add(types.InlineKeyboardButton(text='🔙', callback_data=f'advert-return_{advert_id}'))
        if not inline_buts:
            msg = await call.message.answer('Введите текст кнопки:', reply_markup=AdminPanelKeyboards.back_to_advert_kb(data[2]))
            await AdminStates.advert_kbtext.set()
            await state.update_data(msg=msg, advert_id=advert_id)
        elif type(inline_buts) is dict:
            text = f'Кнопка объявления: \n\nТекст: <code>{inline_buts["text"]}</code> | Тип: <code>{inline_buts["_type"]}</code>' + \
                    f'| Содержимое: {inline_buts["content"]} \n\n<i>Примечание. Кнопки не работают при отправке альбома</i>'
            await call.message.answer(text, reply_markup=kb)
        elif type(inline_buts) is list:
            buts = [f'Текст: <code>{b["text"]}</code> | Тип: <code>{b["_type"]}</code> | Содержимое: {b["content"]}' for b in inline_buts]
            text_buts = '\n'.join(buts)
            text = f'Кнопки объявления:\n\n{text_buts}'
            await call.message.answer(text, reply_markup=kb)
    elif action == 'send':
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='Подтверждаю', callback_data=f'confirm-advert-sending_{advert_id}'))
        text = f"""
<b>Вы уверены что хотите сделать рассылку рекламы <code>{advert_id}</code>?</b>
Подтвердите:
"""
        await call.message.answer(text, reply_markup=kb)
    elif action == 'date':
        advert = await advertising_tables.get_advertising('advert_id', advert_id)
        if advert['sending_date']:
            sending_date = datetime.datetime.strftime(advert['sending_date'], '%H:%M %Y.%m.%d')
        else:
            sending_date = 'Не установлено'
        if advert['sending_status'] == True:
            sending_status = 'Отправлено'
        else:
            sending_status = 'Не отправлено'
        text = f"""
ID рекламы: <code>{advert_id}</code>

Дата отправки: <b>{sending_date}</b>
Статус отправки: <b>{sending_status}</b>

Выберите действие:
"""
        kb = AdminPanelKeyboards.advert_send_date_menu_kb(advert_id)
        kb.add(AdminPanelKeyboards.back_to_advert_button(advert_id))
        await call.message.answer(text, reply_markup=kb)

async def advert_button_add(call: types.CallbackQuery, advertising_tables: AdvertisingTables,
        bot: Bot, logger: logging.Logger, state: FSMContext):
    data = call.data.split('_')
    try: 
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    if data[1] == 'clean-add':
        await advertising_tables.update_advertising(data[2], 'inline_but', None)
    msg = await call.message.answer('Введите текст кнопки:', reply_markup=AdminPanelKeyboards.back_to_advert_kb(data[2]))
    await AdminStates.advert_kbtext.set()
    await state.update_data(msg=msg, advert_id=data[2])


#TODO:
async def advert_kbtext(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, data['msg'].message_id)
    except:
        pass
    await state.update_data(kb_text=message.text)
    kb = AdminPanelKeyboards.get_kb_type_choosing()
    kb.add(keyboards.inclose_button(bot["config"].misc.inclose_text))
    msg = await message.answer('Выберите тип кнопки:', reply_markup=kb)
    await state.update_data(text=message.text, msg=msg)
    await AdminStates.advert_kbtype.set()

async def advert_kbtype(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    _type = call.data.split('-')[1]
    try:
        await bot.delete_message(call.message.chat.id, data['message'].message_id)
    except:
        pass
    msg = await call.message.answer('<b>Введите содержимое кнопки </b>(Ссылка, коллбек, всплывающее окно)')
    await state.update_data(_type=_type, msg=msg)
    await AdminStates.advert_kbcontent.set() #TODO: продолжение

async def advert_kbcontent(message: types.Message, state: FSMContext, 
        advertising_tables: AdvertisingTables, bot: Bot, logger: logging.Logger):
    data = await state.get_data()
    try: 
        await bot.delete_message(message.chat.id, data['msg'].message_id)
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    if data['_type'] == 'popup_message':
        data['_type'] = 'callback_data'
        handler_id = await generate_id_async(len_=3, conn_func=advertising_tables.check_handler_id_exists)
        content = f'popup-message_{handler_id}_{data["advert_id"]}'
        await advertising_tables.create_handler(handler_id, message.text, data['advert_id']) #TODO
    else: 
        content = message.text
    advert = await advertising_tables.get_advertising('advert_id', data['advert_id'])
    logger.info(advert)
    inline_but = {'text': data['text'], '_type': data['_type'], 'content': content}
    if type(advert['inline_buts']) is dict:
        inline_but = [advert['inline_buts'], inline_but]
        inline_but = json.dumps(inline_but)
    elif type(advert['inline_buts']) is list: 
        advert['inline_buts'].append(inline_but)
        inline_but = json.dumps(advert['inline_buts'])
    else:
        inline_but = json.dumps(inline_but)
    await advertising_tables.update_advertising(data['advert_id'], 'inline_buts', inline_but)
    await advert_message_edit_menu(message=message, advert_id=data['advert_id'], bot=bot,
            logger=logger, state=state, advertising_tables=advertising_tables)
    
# ? Move to other module ?
async def popup_message_handler(call: types.CallbackQuery, advertising_tables: AdvertisingTables,
        logger: logging.Logger):
    data = call.data.split('_')
    popup_m = await advertising_tables.take_handler(data[1])
    await call.answer(text=popup_m['message'], show_alert=True)

async def advert_remove(call: types.CallbackQuery, advertising_tables: AdvertisingTables, 
        logger: logging.Logger, bot: Bot):
    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    data = call.data.split('_')
    await advertising_tables.remove_advertising(data[1])
    await advertising_tables.remove_handlers(data[1])
    await call.answer(text='Успешно', show_alert=True)
    

async def find_advert_content(advert_id: str, message: types.Message, advertising_tables: AdvertisingTables, state: FSMContext,
        logger: logging.Logger, bot: Bot):
    if advert_id.isdigit():
        advert = await advertising_tables.get_advertising('advert_id', advert_id)
        if advert: 
            await advert_message_edit_menu(advertising_tables, advert_id=advert['advert_id'], bot=bot,
                    logger=logger, state=state, message=message)
        else:
            kb = keyboards.inclose(bot["config"].misc.inclose_text)
            msg = await message.answer('Объявление не найдено. Повторите ввод:', reply_markup=kb)
            return await state.update_data(msg=msg)
    else:
        kb = keyboards.inclose(bot["config"].misc.inclose_text)
        msg = await message.answer('Айди состоит из чисел. Повторите ввод:', reply_markup=kb)
        return await state.update_data(msg=msg)

async def find_advert_state(message: types.Message, advertising_tables: AdvertisingTables, state: FSMContext, 
        logger: logging.Logger, bot: Bot):
    data = await state.get_data()
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=data['msg'].message_id)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        logger.info(traceback.format_exc())
    await find_advert_content(message.text, message, advertising_tables, state, logger, bot)

async def advert_text(message: types.Message, state: FSMContext, 
        advertising_tables: AdvertisingTables, logger: logging.Logger, bot: Bot):
    data = await state.get_data()
    try:
        await bot.delete_message(message.chat.id, message.from_user.id)
        await bot.delete_message(message.chat.id, data['msg'].message_id)
    except:
        pass
    await advertising_tables.update_advertising(data['advert_id'], 'text', message.text)
    await advert_message_edit_menu(advertising_tables, advert_id=data['advert_id'], logger=logger, bot=bot,
            state=state, message=message)

#TODO deleting_messages
async def advert_media(message: types.Message, state: FSMContext, 
        advertising_tables: AdvertisingTables, logger: logging.Logger, 
        bot: Bot, album: list = None):
    data = await state.get_data()
    if album:
        media_group = types.MediaGroup()
        for obj in album:
            if obj.photo:
                file_id = obj.photo[-1].file_id
            else:
                file_id = obj[obj.content_type].file_id
            try:
                media_group.attach({"media": file_id, "type": obj.content_type})
            except ValueError:
                return await message.answer("Данный тип альбома не поддерживается. Отправьте другое:", 
                        reply_markup=keyboards.inclose(bot["config"].misc.inclose_text))
        await advertising_tables.update_advertising(data['advert_id'], 'media_type', 'media_group')
        media_group = json.dumps(media_group.to_python())
        await advertising_tables.update_advertising(data['advert_id'], 'media', media_group)
    else:
        if message.content_type != 'text':
            media_type = message.content_type
            if message.photo:
                file_id = message.photo[-1].file_id
            else:    
                file_id = message[message.content_type].file_id
            file_id = json.dumps(file_id)
            await advertising_tables.update_advertising(data['advert_id'], 'media_type', media_type)
            await advertising_tables.update_advertising(data['advert_id'], 'media', file_id)
        else:
            return await message.answer('Ошибка. Отправьте медиа:', 
                    reply_markup=keyboards.inclose(bot["config"].misc.inclose_text))
    advert = await advertising_tables.get_advertising('advert_id', data['advert_id'])
    await advert_message_edit_menu(advertising_tables, logger, message=message, bot=bot,
            state=state, advert_id=data['advert_id'])
    try: 
        await bot.delete_message(message.chat.id, data['msg'].message_id)
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

async def newad_header(message: types.Message, advertising_tables: AdvertisingTables, 
        logger: logging.Logger, state: FSMContext):
    max_header_lenght = 27
    if len(message.text) > max_header_lenght:
        return await message.answer(f'<b>! Заголовок слишком длинный, максимальная длина {max_header_lenght}</b>')
    await state.update_data(header=message.text)
    await message.answer('Введите текстовое содержимое рассылки:')
    await AdminStates.newad_text.set()

async def newad_text(message: types.Message, advertising_tables: AdvertisingTables, 
        logger: logging.Logger, state: FSMContext, bot: Bot):
    await state.update_data(text=message.text)
    data = await state.get_data()
    advert_id = await generate_id_async(4, advertising_tables.check_for_id)
    await state.update_data(advert_id=advert_id)
    await advertising_tables.add_advertising(advert_id=advert_id, advert_header=data['header'],
            text=data['text'])
    await advert_message_edit_menu(advertising_tables, logger=logger, bot=bot, message=message, state=state) 

async def advert_send(call: types.CallbackQuery, advertising_tables: AdvertisingTables, 
        user_tables: UserTables, logger: logging.Logger, bot: Bot):
    try: 
        await bot.delete_message(call.from_user.id, call.message.message_id)
    except:
        pass
    advert = await advertising_tables.get_advertising('advert_id', call.data.split('_')[1])
    users = await user_tables.take_all_users()
    for user in users:
        try:
            await send_advert_to_user(advert, user['user_id'], bot)
        except:
            logger.error(traceback.format_exc())
    
# All admin commands starting with '!'
async def admin_commands(message: types.Message, bot: Bot,
        logger: logging.Logger, user_tables: UserTables, 
        modhistory_tables: ModeratingHistoryTables, state: FSMContext,
        advertising_tables: AdvertisingTables):
    try: 
        await state.finish()
    except:
        pass
    data = message.text.split(' ')
    action = data[0]
    if action == '!ban':
        if len(data) < 2:
            return await message.reply('Неверный синтаксис. Необходимо передать больше иноформации. /adm для справки.') 
        await admin_panel.ban_user(user=data[1], user_tables=user_tables, 
                bot=bot, modhistory_tables=modhistory_tables, 
                num_of=safe_list_get(data, 2, None), unit=safe_list_get(data, 3, None), 
                message=message, logger=logger) #TODO
    elif action == '!unban':
        if len(data) < 2:
            return await message.reply('Неверный синтаксис. Необходимо передать больше иноформации. /adm для справки.') 
        await admin_panel.unban_user(user=data[1], user_tables=user_tables, modhistory_tables=modhistory_tables, 
                bot=bot, message=message, logger=logger)
    elif action == '!adm_send_message':
        if len(data) < 3:
            return await message.reply('Неверный синтаксис. Необходимо передать больше иноформации. /adm для справки.') 
        text = ' '.join(data[2:])
        await admin_panel.message_to_user(user=data[1], user_tables=user_tables, bot=bot,
                message_text=text, message=message, logger=logger)
    elif action == '!info': #TODO: recieve info with reply 
        if len(data) < 2:
            return await message.reply('Неверный синтаксис. Необходимо передать больше иноформации. /adm для справки.')
        content = await admin_panel.get_user_info(data[1], user_tables, bot, message, logger)
        kb = AdminPanelKeyboards.get_user_moderate_keyboard(data[1])
        kb.add(keyboards.inclose_button(bot["config"].misc.inclose_text))
        await message.answer(content, reply_markup=kb)
    elif action == '!new_ad': #new advertising message
        await message.answer('Введите заголовок для рассылки (для удобства отображения):')
        await AdminStates.newad_header.set()
    elif action == '!advert':
        if len(data) < 2:
            kb = keyboards.inclose(bot["config"].misc.inclose_text)
            msg = await message.answer('Введите айди объявления для редактирования: ', reply_markup=kb)
            await state.update_data(msg=msg)
            await AdminStates.find_advert.set()
        else:
            await find_advert_content(data[1], message, advertising_tables, state, logger, bot) 
    elif action == '!edit_user':
        pass #TODO editing user by "!edit_user <key> <value>" format

async def advert_sending_date_actions(call: types.CallbackQuery, state: FSMContext, logger: logging.Logger):
    data = call.data.split('_')
    action, advert_id = data[1], data[2]
    if action == "changing":
        msg = await call.message.answer("Введите дату отправки в формате - \n<b>ЧАС:МИНУТА ГОД.МЕСЯЦ.ДЕНЬ</b>\n\nлибо" +
                "\n<b>ЧАС:МИНУТА</b>, если хотите отправить сегодня", reply_markup=AdminPanelKeyboards.back_to_advert_kb(advert_id))
        await state.update_data(msg=msg, advert_id=advert_id)
        await AdminStates.advert_sending_date.set()
    elif action == "cancel":
        pass

async def advert_changing_sending_date(message: types.Message, advertising_tables: AdvertisingTables,
        state: FSMContext, bot: Bot, logger: logging.Logger):
    data = await state.get_data()
    message_data = message.text.split(' ')
    try:
        await bot.delete_message(data['msg'].chat.id, data['msg'].message_id)
    except:
        pass
    text_blocks = message.text.split(' ')
    block1 = text_blocks[0]
    try:
        block2 = text_blocks[1]
    except IndexError:
        block2 = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y.%m.%d')
    final_date_str = block1 + ' ' + block2
    try:
        final_date = datetime.datetime.strptime(final_date_str, '%H:%M %Y.%m.%d')
    except ValueError:
        text = """
<b>ОШИБКА. Неверный формат времени, повторите попытку</b>

Введите дату отправки в формате - 
<b>ЧАС:МИНУТА ГОД.МЕСЯЦ.ДЕНЬ</b>

либо 
<b>ЧАС:МИНУТА</b>, если хотите отправить сегодня
"""
        msg = await message.answer(text, reply_markup=AdminPanelKeyboards.back_to_advert_kb(data['advert_id']))
        return await state.update_data(msg=msg)
    await advertising_tables.update_advertising(data['advert_id'], 'sending_date', final_date)
    await advertising_tables.update_advertising(data['advert_id'], 'sending_status', False)
    advert = await advertising_tables.get_advertising('advert_id', data['advert_id'])
    logger.info(advert['sending_date'])
    await message.answer('Отправка успешно назначена на <code>' + final_date_str + '</code>')
    await advert_message_edit_menu(advertising_tables, logger, state, bot, message=message, advert_id=data['advert_id'])

#debug function
async def check_call(call: types.CallbackQuery, logger: logging.Logger):
    logger.info(call.to_python())


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_panel_start, commands=["adm"], state="*", is_admin=True)
    dp.register_callback_query_handler(admin_panel_actions, lambda call: call.data.startswith('adm-panel_'), state='*', is_admin=True)
    dp.register_callback_query_handler(admin_actions, lambda call: call.data.startswith('adm-action_'), state='*', is_admin=True)

    dp.register_message_handler(find_user_state, state=AdminStates.find_user)

    dp.register_callback_query_handler(admin_user_actions, lambda call: call.data.startswith('adm-user_'), state='*', is_admin=True)

    dp.register_message_handler(admin_commands, lambda message: message.text.startswith('!'), state='*', is_admin=True)

    dp.register_message_handler(newad_header, state=AdminStates.newad_header, is_admin=True)
    dp.register_message_handler(newad_text, state=AdminStates.newad_text, is_admin=True)

    dp.register_callback_query_handler(advert_edit_actions, lambda call: call.data.startswith('advertedit_'), state='*')
    dp.register_message_handler(advert_media, state=AdminStates.advert_media, content_types=types.ContentTypes.ANY)
    dp.register_message_handler(advert_text, state=AdminStates.advert_text)

    dp.register_callback_query_handler(admin_advertpanel, lambda call: call.data.startswith('advertpanel_'))

    dp.register_message_handler(find_advert_state, state=AdminStates.find_advert)

    dp.register_callback_query_handler(advert_remove, lambda call: call.data.startswith('confirmadremove_'))

    dp.register_message_handler(advert_kbtext, state=AdminStates.advert_kbtext)
    dp.register_callback_query_handler(advert_kbtype, state=AdminStates.advert_kbtype)
    dp.register_message_handler(advert_kbcontent, state=AdminStates.advert_kbcontent)

    dp.register_callback_query_handler(popup_message_handler, lambda call: call.data.startswith('popup-message_'), state='*')

    dp.register_callback_query_handler(advert_button_add, lambda call: call.data.startswith('advert-kb_'))

    dp.register_callback_query_handler(advert_send, lambda call: call.data.startswith('confirm-advert-sending_'))
    #dp.register_callback_query_handler(check_call)

    dp.register_callback_query_handler(advert_sending_date_actions, lambda call: call.data.startswith('advert-send-date_'))

    dp.register_message_handler(advert_changing_sending_date, state=AdminStates.advert_sending_date)
