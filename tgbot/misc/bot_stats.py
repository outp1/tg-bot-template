from typing import List, Optional
import random
import datetime

import pytz

from tgbot.models.users import User
from config import config


def get_users_regs_number(timedelta: int, users_list: List[User]):
    tz = pytz.timezone(config.program.timezone)
    today = datetime.datetime.now(tz)
    return len(list(
        filter(
            lambda user: user.created_at.replace(tzinfo=tz)
            >= (today - datetime.timedelta(timedelta)),
            users_list,
        )
    ))


def get_sorted_users(
    users_list: List[User],
    num_of_users: int = 5,
    sort_attr: Optional[str] = None,
    reverse=False,
):
    if not sort_attr:
        sort_attr = "created_at"
    users_list.sort(key=lambda user: getattr(user, sort_attr), reverse=reverse)
    if len(users_list) <= num_of_users:
        return users_list
    return users_list[:num_of_users]


def get_list_of_random_users(
    users_list: List[User],
    num_of_users: int = 5,
):
    copy_list = users_list.copy()
    if len(users_list) < num_of_users:
        return users_list
    else:
        return random.sample(copy_list, num_of_users)
