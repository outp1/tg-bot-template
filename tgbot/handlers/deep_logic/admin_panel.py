import datetime
import logging
import traceback

import pytz
from aiogram import Bot, types
from aiogram.dispatcher.storage import FSMContext

from tgbot.misc import statisticer
from tgbot.models import UserTables, ModeratingHistoryTables, AdvertisingTables
from tgbot.data.db_tables import reg_date_index


async def format_user_info_to_text(user_info: dict, logger: logging.Logger = logging):
    # managing_history = '\n'.join(user_info["user_history"])
    managing_history = user_info["user_history"]
    if managing_history:
        if len(managing_history) >= 8:
            managing_history = managing_history[len(managing_history) - 8 :]
        formated_history = "\n".join(managing_history[::-1])
    else:
        formated_history = ""
    if user_info["referal_id"]:
        ref_user = await bot.get_chat(user["referal_id"])
        referal = f"Пригласивший: <code>{ref_user.mention}</code>"
    else:
        referal = f"Пригласивший: никто"
    text = f"""
<b>Данные пользователя - {user_info["mention"]}</b>

ID: <code>{user_info["user_id"]}</code>
Дата регистрации: <code>{user_info["reg_date"]}</code>
Рейтинг: <code>{user_info["rating"]}</code>
{referal}

История модерации:
{formated_history}

<i>Выберите действие:</i>
"""
    return text


# TODO
async def take_stats_content(
    user_tables: UserTables,
    logger: logging.Logger = logging,
    bot_name: str = "Без имени",
):
    today = datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y")
    users_list = await user_tables.take_all_users()
    statistic = statisticer.BotStatistic(
        users_list, reg_date_index=reg_date_index, logger=logger
    )
    month_regs = await statistic.regs_number(30)
    today_regs = await statistic.regs_number(1)
    fmt_last_users = (
        "<code>{reg_date:%m-%d %H-%M}</code> - {mention} - реф. {referal_id}"
    )
    last_4_users = await statistic.sorted_users_strings(fmt_last_users, 4, "reg_date")
    last_3_adm_actions = "<code>@mdaroff - 25.07 9:44 - Новая рекламный пост на 12:20</code> \n<code>@mdaroff - 25.07 8:13 - Подделка статистики </code>"  # TODO
    last_4_users = "\n".join(last_4_users)
    #    for user in users_list:
    #        if user['reg_date'].strftime('%Y-%m-%d') == today.strftime('%Y-%m-%d'):
    #            today_regs += 1
    #        if user['reg_date'] <= (today - datetime.timedelta(days=30)):
    #            month_regs += 1
    text = f"""
Статистика бота <b><i>{bot_name}</i></b> на <b><i>{today}</i></b>

Пользователей - <code>{len(users_list)}</code>

<b>Новые пользователи</b>
Сегодня - <code>{today_regs}</code>
За месяц - <code>{month_regs}</code>
- Последние -
{last_4_users}
- -

Последние действия администрации:
{last_3_adm_actions}

<i>Лучшие телеграмм боты - @mdaroff</i>
"""
    return text


# TODO
async def take_users_content(user_tables: UserTables, logger: logging.Logger = logging):
    users_list = await user_tables.take_all_users()
    statistic = statisticer.BotStatistic(users_list, logger=logger)
    best_users = await statistic.list_of_the_best(
        20, "reg_date", "rating", logger=logger
    )
    best_users_strings = []
    for user in best_users:
        best_users_strings.append(
            f'{user["mention"]} <code>{user["user_id"]}</code> - д.р: <code>{user["reg_date"].strftime("%d-%m-%Y")}</code> - рейтинг: {user["rating"]}'
        )
    best_users_text = "\n".join(best_users_strings)
    text = f"""

<b>Топ пользователей:</b>
{best_users_text}

<i>Выберите действие:</i>
"""
    return text


async def take_advert_content(
    advertising_tables: AdvertisingTables, logger: logging.Logger
):
    all_ads = await advertising_tables.get_all_advertisements()
    for ad in all_ads:
        logger.info(f"{ad['sending_date']} - {type(ad['sending_date'])}")
    try:
        all_ads.sort(
            key=lambda x: x["sending_date"] if x["sending_date"] else x["advert_id"],
            reverse=False,
        )  # TODO: reverse or no?
    except TypeError:
        pass
    all_ads_text = []
    for ad in all_ads[:7]:
        if ad["sending_date"] is None:
            sending_date = "не установлена"
        else:
            sending_date = ad["sending_date"]
        if ad["sending_status"] is False:
            sending_status = "⏳"
        else:
            sending_status = "✅"
        value = f"<code>{ad['advert_id']} | {ad['advert_header']} | {sending_date} | {sending_status}</code>"
        all_ads_text.append(value)
    ads_list = "\n".join(all_ads_text)
    text = f"""
Ближайшая реклама
{ads_list}

<b>Выберите действие:</b>
"""
    return text


async def take_find_user_content(
    message: types.Message,
    user_tables: UserTables,
    state: FSMContext,
    bot: Bot,
    logger: logging.Logger = logging,
):
    search_means = message.text
    if search_means.isdigit():
        user = await user_tables.take_user("user_id", search_means)
        await state.finish()
    elif search_means.startswith("@"):
        user = await user_tables.take_user("mention", search_means)
        await state.finish()
    else:
        return None
    text = await format_user_info_to_text(user)
    return text


# TODO: user_story action
async def ban_user(
    user: str,
    user_tables: UserTables,
    bot: Bot,
    message: types.Message,
    modhistory_tables: ModeratingHistoryTables,
    num_of: str = None,
    unit: str = None,
    logger: logging.Logger = logging,
):
    now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
    now_str = now.strftime("%Y-%m-%d %H:%M")
    if not num_of.isdigit():
        return await message.answer("Неверный синтаксис, для справки введите /adm")
    if num_of:
        if unit == "h":
            block_time = datetime.timedelta(hours=int(num_of))
        elif unit == "m":
            block_time = datetime.timedelta(minutes=int(num_of))
        elif unit == "d":
            block_time = datetime.timedelta(days=int(num_of))
        else:
            block_time = datetime.timedelta(minutes=int(num_of))
    else:
        block_time = datetime.timedelta(days=8000)
    user_info = await user_tables.take_user("user_id", user)
    from_user = await user_tables.take_user("user_id", str(message.from_user.id))
    try:
        if user_info["unbanned_date"] >= now:
            unbanned_date = user_info["unbanned_date"] + block_time
            status = "Продление"
        else:
            status = "Новая"
            unbanned_date = now + block_time
    except TypeError:  # if user_info['unbanned_date'] is None
        status = "Новая"
        unbanned_date = now + block_time
    logger.info(unbanned_date)
    unbanned_date_text_format = unbanned_date.strftime("%Y-%m-%d %H:%M")
    user_profile = await bot.get_chat(user)
    bot["banned_users"].append(user)
    await user_tables.change_ban_status_user(user, unbanned_date=unbanned_date)
    if status == "Продление":
        await user_tables.add_user_history(
            user,
            f"<code>{now_str} | {message.from_user.mention} | Продление блокировки до {unbanned_date_text_format}</code>",
        )
        await message.answer(
            f'<a href="t.me/{user_profile.mention[1:]}">Пользователю</a> продлена блокировка до {unbanned_date_text_format}',
            disable_web_page_preview=True,
        )
        await bot.send_message(
            user, f"Вам продлили блокировку до <code>{unbanned_date_text_format}</code>"
        )
    elif status == "Новая":
        await user_tables.add_user_history(
            user,
            f"<code>{now_str} | {message.from_user.mention} | Блокировка до {unbanned_date_text_format}</code>",
        )
        await message.answer(
            f'<a href="t.me/{user_profile.mention[1:]}">Пользователь</a> заблокирован до {unbanned_date_text_format}',
            disable_web_page_preview=True,
        )
        await bot.send_message(
            user, f"Вам дали блокировку до <code>{unbanned_date_text_format}</code>"
        )
    action_to_modhistory = (
        f"Блокировка пользователя {user_profile.mention} до {unbanned_date_text_format}"
    )
    await modhistory_tables.add_entry_to_history(
        str(message.from_user.id), from_user["role"], action_to_modhistory, date=now
    )


async def unban_user(
    user: str,
    user_tables: UserTables,
    bot: Bot,
    message: types.Message,
    modhistory_tables: ModeratingHistoryTables,
    logger: logging.Logger = logging,
):
    now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
    now_str = now.strftime("%Y-%m-%d %H:%M")
    user_info = await user_tables.take_user("user_id", user)
    user_profile = await bot.get_chat(user)
    from_user = await user_tables.take_user("user_id", str(message.from_user.id))
    if user_info["unbanned_date"] <= now:
        return await message.answer(
            f'<a href="t.me/{user_profile.mention[1:]}">Пользователь</a> не является заблокированным',
            disable_web_page_preview=True,
        )
    await user_tables.add_user_history(
        user,
        f"<code>{now_str} | {message.from_user.mention} | Ручное снятие блокировки</code>",
    )
    action_to_modhistory = (
        f"Ручное снятие блокировки пользователю {user_profile.mention}"
    )
    await modhistory_tables.add_entry_to_history(
        str(message.from_user.id), from_user["role"], action_to_modhistory, date=now
    )
    await user_tables.change_ban_status_user(user, unban=True)

    while True:  # Удаление всех совпадений из спиcка #TODO: отдельная функция
        try:
            bot["banned_users"].remove(user)
        except ValueError:
            break

    await message.answer(
        '<a href="t.me/{user_profile.mention[1:]}">Пользователь</a> разблокирован',
        disable_web_page_preview=True,
    )
    await bot.send_message(
        chat_id=user,
        text=f'<a href="t.me/{message.from_user.mention[1:]}">Администратор</a> снял вашу блокировку',
        disable_web_page_preview=True,
    )


async def get_user_info(
    user: str,
    user_tables: UserTables,
    bot: Bot,
    message: types.Message,
    logger: logging.Logger = logging,
):
    user_info = await user_tables.take_user("user_id", user)
    message_text = await format_user_info_to_text(user_info)
    return message_text


async def message_to_user(
    user: str,
    user_tables: UserTables,
    bot: Bot,
    message_text: str,
    message: types.Message,
    logger: logging.Logger = logging,
):
    if not message_text:
        raise BaseException("No message to send")
    # TODO: do this action need to save in actions history?
    # user_tables.add_user_history(user, f'<code>{message.from_user.mention} отправил сообщение с текстом {message_text}</code>')
    text = f"""
<b>Администратор #{message.from_user.mention[1:]} отправил вам личное сообщение:</b>

{message_text}
"""
    await bot.send_message(chat_id=user, text=text)
    user_chat = await bot.get_chat(chat_id=user)
    await message.answer(f"Сообщение отправлено пользователю {user_chat.mention}")


async def get_content_advertpanel_full(
    call: types.CallbackQuery,
    advertising_tables: AdvertisingTables,
    logger: logging.Logger,
):
    adverts = await advertising_tables.get_all_advertisements()
    ads_list = []
    for ad in adverts:
        if ad["sending_date"] is None:
            sending_date = "не установлена"
        else:
            sending_date = ad["sending_date"]
        if ad["sending_status"] is False:
            sending_status = "⏳"
        else:
            sending_status = "✅"
        ads_list.append(
            f"<code>{ad['advert_id']} | {ad['advert_header']} | {sending_date} | {sending_status}</code>"
        )
    ads_text = "\n".join(ads_list)
    text = f"""
<b>Список всех объявлений:</b>

{ads_text}
"""
    return text
