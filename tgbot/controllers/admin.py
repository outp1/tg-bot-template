import re
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.orm import Session

import pytz

from tgbot import keyboards
from tgbot.keyboards.inline import get_admin_panel_keyboard
from config import config
from tgbot.models.users import UsersRepository
from tgbot.models.adverts import AdvertisementsRepository
from tgbot.models.users import User
from tgbot.misc.bot_stats import (
    get_users_regs_number,
    get_sorted_users,
    get_list_of_random_users,
)


class AdminController:
    def __init__(self, session: Session, db_repository: dict):
        self.session = session
        self.db_repository = db_repository
        self.users_repo = UsersRepository(self.session, self.db_repository)
        self.adverts_repo = AdvertisementsRepository(self.session, self.db_repository)

    async def start(self):
        kb = get_admin_panel_keyboard()
        kb.add(keyboards.inclose_button(config.misc.inclose_text))
        return "Hello, admin!", kb

    async def stats_panel(self):
        day = datetime.now(pytz.timezone(config.program.timezone)).strftime("%d.%m.%Y")
        users_list = self.users_repo.list()
        months_regs = get_users_regs_number(30, users_list)
        today_regs = get_users_regs_number(1, users_list)
        last_4_users = get_sorted_users(users_list, 4, "created_at", True)
        last_3_adm_actions = "soon..."
        last_4_users_text = [
            "<code>{}</code> | <code>{:%m.%d %H:%M} - {}</code>".format(
                user.id, user.created_at, user.username
            )
            for user in last_4_users
        ]
        text = (
            "Statistics of the <b>{}</b> for <b><i>{}</i></b>"
            "\n\nTotal users count - <code>{}</code>"
            "\n\n<b>New users</b>\nToday - <code>{}</code>\nFor a month - {}"
            "\n- Last registered users -\n{}"
            "\n\nLast admin actions:\n{}".format(
                config.tg_bot.bot_name,
                day,
                len(users_list),
                today_regs,
                months_regs,
                "\n".join(last_4_users_text),
                last_3_adm_actions,
            )
        )
        kb = InlineKeyboardMarkup()
        return text, kb

    async def users_panel(self):
        day = datetime.now(pytz.timezone(config.program.timezone)).strftime("%d.%m.%Y")
        users_list = self.users_repo.list()
        random_users = get_list_of_random_users(users_list, 7)
        random_users_text = []
        for user in random_users:
            random_users_text.append(
                "<code>{} - {} - registered at {}</code>".format(
                    user.id, user.username, user.created_at
                )
            )
        text = (
            "The <b>{}</b> users panel for <b><i>{}</i></b>\n\n"
            "<b>Random list of users:</b>\n{}".format(
                config.tg_bot.bot_name, day, "\n".join(random_users_text)
            )
        )
        return text, InlineKeyboardMarkup()

    async def adverts_panel(self):
        day = datetime.now(pytz.timezone(config.program.timezone)).strftime("%d.%m.%Y")
        all_ads = self.adverts_repo.list()
        all_ads_text = [
            f"<code>{ad.id}</code> | <code>{ad.header} | {ad.sending_dates}</code>"
            for ad in all_ads
        ]
        text = (
            "The advert panel of the <b>{}</b> on <b><i>{}</i></b>\n\n"
            "Upcoming advertisements:\n{}".format(
                config.tg_bot.bot_name, day, "\n".join(all_ads_text)
            )
        )
        kb = InlineKeyboardMarkup()
        return text, kb

    async def get_user_info_panel(self, user: User):
        return (
            "<b>User Information <code>{}</code> (@{})</b>\n\n"
            "Registration date: <code>{}</code>\n"
            "Ban Information: <code>{}</code>\n".format(
                user.id,
                user.username,
                user.created_at.strftime("%Y-%m-%d %H:%M"),
                user.ban_date,
            ),
            InlineKeyboardMarkup(),
        )

    async def find_user(self, text):
        # Check if the text is a Telegram ID
        if re.match(r"^\d+$", text):
            user = self.users_repo.get_by_id(text)
            if user:
                return await self.get_user_info_panel(user)
        # Check if the text is a Telegram username
        elif re.match(r"^[a-zA-Z0-9_]+$", text):
            user = self.users_repo.get_by_username(text)
            if user:
                return await self.get_user_info_panel(user)
        # If the text is neither an ID nor a username
        else:
            return "Not a Telegram ID or username was specified", InlineKeyboardMarkup()
        return "User was not found", InlineKeyboardMarkup()
