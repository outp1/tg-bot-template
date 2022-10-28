from datetime import datetime
import logging

import pytz
from psycopg2 import extras

from .pgsqlighter import DatabaseConnection


class ModeratingHistoryTables(DatabaseConnection):

    def __init__(self, db_name: str, auth: dict, tables: list, logger: logging.Logger = logging):
        super().__init__(db_name, auth, tables)

    async def get_all_history(self):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute('SELECT * FROM moderating_history')
                return cursor.fetchall()
            
    async def add_entry_to_history(self, user_id, role, action, date):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute('INSERT INTO moderating_history (user_id, role, action, date) VALUES (%s, %s, %s, %s)', (user_id, role, action, date))


class AdvertisingTables(DatabaseConnection):

    def __init__(self, db_name: str, auth: dict, tables: list, logger: logging.Logger = logging):
        super().__init__(db_name, auth, tables)

    async def get_all_advertisements(self):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute('SELECT * FROM advertising')
                return cursor.fetchall()

    async def get_advertising(self, key, value):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute(f'SELECT * FROM advertising WHERE {key} = %s', (value,))
                return cursor.fetchone()


    async def add_advertising(self, advert_id, advert_header, text, media = None,
            media_type = None, inline_buts = None, 
            sending_date = None, sending_status = False):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute('INSERT INTO advertising ' + \
                        '(advert_id, advert_header, text, media, media_type, inline_buts, sending_date, sending_status) ' + \
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (advert_id, advert_header, text, media, 
                            media_type, inline_buts, sending_date, sending_status))

    async def update_advertising(self, advert_id, key, value):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute(f'UPDATE advertising SET {key} = %s WHERE advert_id = %s', (value, advert_id))

    async def check_for_id(self, _id):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute(f'SELECT * FROM advertising WHERE advert_id = %s', (_id,))
                return cursor.fetchone()

    async def remove_advertising(self, advert_id):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute(f'DELETE FROM advertising WHERE advert_id = %s', (advert_id,))        

    # -- POP-UP MESSAGE HANDLERS --

    async def take_handler(self, handler_id):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute('SELECT * FROM advertising_handlers WHERE handler_id = %s', (handler_id,))
                return cursor.fetchone()

    async def create_handler(self, handler_id, message, advert_id):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute('INSERT INTO advertising_handlers (handler_id, message, advert_id) VALUES (%s, %s, %s)', 
                        (handler_id, message, advert_id))

    async def remove_handlers(self, advert_id):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute('DELETE FROM advertising_handlers WHERE handler_id = %s', (handler_id,))

    async def check_handler_id_exists(self, handler_id):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute(f'SELECT * FROM advertising_handlers WHERE handler_id = %s', (handler_id,))
                return cursor.fetchone()

    # -- --
