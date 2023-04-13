import datetime
import logging

import pytz
from aiogram import Bot, types
from aiogram.dispatcher.storage import FSMContext

from config import config
from tgbot.misc.botstats import get_regs
from tgbot.models import UserTables


# TODO
async def take_stats_content(
    user_tables: UserTables,
    logger: logging.Logger = logging.getLogger(),
    bot_name: str = "Без имени",
):
    today = datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y")
    users_list = await user_tables.take_all_users()
    statistic = statisticer.BotStatistic(users_list, logger=logger)
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
    best_users = await statistic.list_of_the_best(20, "reg_date")
    best_users_strings = []
    for user in best_users:
        best_users_strings.append(
            f'{user["mention"]} <code>{user["user_id"]}</code> - д.р: <code>{user["reg_date"].strftime("%d-%m-%Y")}</code> - рейтинг: {user["rating"]}'
        )
    best_users_text = "\n".join(best_users_strings)
    text = f"""
Лучшие пользователи бота <b>{config.tg_bot.bot_name}</b>:
{best_users_text}

<i>Выберите действие:</i>
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
    if user["referal_id"]:
        ref_user = await bot.get_chat(user["referal_id"])
        referal = f"Пригласивший: <code>{ref_user.mention}</code>"
    else:
        referal = f"Пригласивший: никто"
    text = f"""
<b>Данные пользователя - {user["mention"]}</b>

ID: <code>{user["user_id"]}</code>
Дата регистрации: <code>{user["reg_date"]}</code>
Рейтинг: <code>{user["rating"]}</code>
{referal}

<i>Выберите действие:</i>
"""
    return text


# TODO
async def ban_user(
    user: str,
    user_tables: UserTables,
    bot: Bot,
    num_of: str = None,
    unit: str = None,
    logger: logging.Logger = logging,
):
    now = datetime.datetime.now(tz=pytz.timezone("Europe/Moscow"))
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
    unbanned_date = now + block_time
    unbanned_date_text_format = unbanned_date.strftime("%d-%m-%Y %H:%M")
    logger.info(f"DATE: {unbanned_date}")
    logger.info(f"USER: {user}")
    await user_tables.ban_user(user, unbanned_date)
    await bot.send_message(
        user, f"Вам прилетела блокировка до <code>{unbanned_date_text_format}</code>"
    )
