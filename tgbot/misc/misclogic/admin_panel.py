import datetime
import logging

import pytz

from tgbot.misc import statisticer
from tgbot.models import UserTables


#TODO
async def take_stats_content(user_tables: UserTables, logger: logging.Logger('AdmPanel'),
        bot_name: str = 'Без имени'):
    today = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y')
    users_list = await user_tables.take_all_users()
    statistic = statisticer.BotStatistic(users_list, logger=logger)
    month_regs = await statistic.regs_number(30)
    today_regs = await statistic.regs_number(1)
    fmt_last_users = '<code>{reg_date:%m-%d %H-%M}</code> - {mention}'
    last_4_users = await statistic.last_users_strings(fmt_last_users, 4, 'reg_date')
    last_4_users = '\n'.join(last_4_users)
    logger.info(last_4_users)
#    for user in users_list:
#        if user['reg_date'].strftime('%Y-%m-%d') == today.strftime('%Y-%m-%d'):
#            today_regs += 1
#        if user['reg_date'] <= (today - datetime.timedelta(days=30)):
#            month_regs += 1
    text = f"""
Статистика бота <b><i>{bot_name}</i></b> на <b><i>{today}</i></b>

<b>Новые пользователи</b>
Сегодня - <code>{today_regs}</code>
За месяц - <code>{month_regs}</code>
- Последние -
{last_4_users}
- -

<i>Лучшие телеграмм боты - @mdaroff</i>
"""
    return text

#TODO
async def take_users_content():
    return 'Some result \nChoose action:'
