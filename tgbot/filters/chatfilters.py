from aiogram.dispatcher.filters import BoundFilter
from aiogram import types

from typing import Optional

class PrivateFilter(BoundFilter):
    key = 'is_private'

    def __init__(self, is_private: Optional[bool] = None):
        self.is_private = is_private

    async def check(self, obj):
        if self.is_private is None:
            return False
        return (obj.from_user.id == obj.chat.id) == self.is_private 



