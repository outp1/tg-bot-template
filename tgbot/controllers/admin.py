import re
from datetime import datetime, timedelta
from typing import Optional, Union

import pytz
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from config import config
from tgbot.keyboards.inline import get_admin_panel_keyboard, get_user_moderate_keyboard
from tgbot.misc.bot_stats import (
    get_list_of_random_users,
    get_sorted_users,
    get_users_regs_number,
)
from tgbot.misc.exceptions import EntityToEditNotFoundError
from tgbot.models.adverts import AdvertisementsRepository
from tgbot.models.users import User, UsersRepository


class AdminController:
    def __init__(self, session: Session, db_repository: dict, bot: Bot):
        self.session = session
        self.db_repository = db_repository
        self.users_repo = UsersRepository(self.session, self.db_repository)
        self.adverts_repo = AdvertisementsRepository(self.session, self.db_repository)
        self.bot = bot

    async def start(self):
        kb = get_admin_panel_keyboard()
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
            get_user_moderate_keyboard(user.id),
        )

    async def find_user(self, text) -> Optional[User]:
        # Check if the text is a Telegram ID
        if re.match(r"^\d+$", str(text)):
            return self.users_repo.get_by_id(text)
        # Check if the text is a Telegram username
        elif re.match(r"^[a-zA-Z0-9_]+$", str(text)):
            return self.users_repo.get_by_username(text)

    async def find_user_action(self, text):
        user = await self.find_user(text)
        if user:
            return await self.get_user_info_panel(user)
        else:
            return "User was not found", InlineKeyboardMarkup()

    async def ban_user(self, user: User, ban_time: Union[str, timedelta], description):
        if isinstance(ban_time, str):
            duration_unit = {"m": "minutes", "h": "hours", "d": "days"}
            if ban_time[-1] in duration_unit:
                unit = duration_unit[ban_time[-1]]
                duration = int(ban_time[:-1])
            else:
                unit = duration_unit["m"]
                duration = int(ban_time)
            ban_time = timedelta(**{unit: duration})
        elif not ban_time:
            ban_time = timedelta(weeks=1200)
        if isinstance(user.unbanned_date, datetime):
            user.unbanned_date += ban_time
        else:
            user.unbanned_date = ban_time + datetime.now(
                tz=pytz.timezone(config.program.timezone)
            )
        self.users_repo.persist(user)
        await self.bot.send_message(
            user.id,
            "<b>You were banned by the bot administration for the reason: <i>{}</i>. "
            "The lock will be lifted on {:%Y-%m-%d at %H:%M}</b>".format(
                description, user.unbanned_date
            ),
        )

    async def edit_user(self, user: User):
        try:
            self.users_repo.persist(user)
            self.session.commit()
        except AssertionError:
            raise EntityToEditNotFoundError

    async def ban_user_action(self, search_user, ban_time, description):
        user = await self.find_user(search_user)
        if user:
            await self.ban_user(user, ban_time, description)
            return (
                "<b>User @{} has been banned until {:%Y-%m-%d %H-%M}</b>".format(
                    user.username, user.unbanned_date
                ),
                InlineKeyboardMarkup(),
            )
        else:
            return "User to ban was not found", InlineKeyboardMarkup()

    async def edit_user_action(self, search_user, key, value):
        user = await self.find_user(search_user)
        if not user:
            return "User to edit was not found", InlineKeyboardMarkup()
        if key == "id":
            return "Primary key can't be edited", InlineKeyboardMarkup()
        if hasattr(user, key):
            setattr(user, key, value)
        else:
            return "Error! Key to edit does not exist.", InlineKeyboardMarkup()
        try:
            await self.edit_user(user)
        except DataError:
            self.session.rollback()
            return "Error! This key can't be edited in this way", InlineKeyboardMarkup()
        return (
            f"Successfully edited <code>{key}</code> to <code>{value}</code> "
            f"for a user with id <code>{user.id}</code>"
        ), InlineKeyboardMarkup()
