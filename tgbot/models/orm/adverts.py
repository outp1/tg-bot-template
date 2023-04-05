from datetime import datetime

from aiogram.types import InlineKeyboardMarkup
from sqlalchemy import Column, String, JSON, ForeignKey

from .base import BaseID, BaseModel
from .users import UserModel


class AdvertModel(BaseModel):
    __tablename__ = "advertisements"

    header = Column(String, nullable=False)
    content = Column(JSON, nullable=False, default={"text": "Empty message"})
    reply_markup = Column(
        JSON, nullable=False, default=InlineKeyboardMarkup().as_json()
    )
    sending_dates = Column(JSON, nullable=True)
    created_by = Column(BaseID, ForeignKey(UserModel.id), nullable=False)

    def __init__(
        self, id, header, content, created_by, sending_dates=None, reply_markup=None
    ):
        self.id = id
        self.header = header
        self.content = content
        self.created_by = created_by
        self.reply_markup = reply_markup or InlineKeyboardMarkup().as_json()

        if sending_dates is None:
            self.sending_dates = None
        else:
            self.sending_dates = {
                datetime.strftime(key, "%Y-%m-%d %H:%M:%S"): value
                for key, value in sending_dates.items()
            }


class AdvertHandlerModel(BaseModel):
    __tablename__ = "advertisements_handlers"

    advert_id = Column(BaseID, ForeignKey(AdvertModel.id))
    message = Column(String)
