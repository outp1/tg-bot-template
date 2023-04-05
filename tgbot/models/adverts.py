from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from aiogram.types import InlineKeyboardMarkup

from .orm.adverts import AdvertModel

from .orm.base import Repository

from .users import UserID

AdvertID = int


@dataclass
class Advert:
    id: AdvertID
    header: str
    content: dict
    created_by: UserID
    reply_markup: dict = field(
        default_factory=lambda: InlineKeyboardMarkup().to_python()
    )
    sending_dates: Optional[dict] = None


@dataclass
class AdvertHandler:
    advert_id: AdvertID
    message: str


class AdvertisementsRepository(Repository):
    def __init__(self, session: Session, identity_map=None):
        self.session = session
        self.repository_name = "adverts"
        self._identity_map = identity_map or {self.repository_name: {}}
        self.entity_class = Advert
        self.model_class = AdvertModel
