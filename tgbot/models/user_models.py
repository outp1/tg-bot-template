import datetime
import json
import logging

import pytz
from psycopg2 import extras

from tgbot.misc.identifier_classes import UserId
from .pgsqlighter import DatabaseConnection

#TODO: document this module

class UserTables(DatabaseConnection): 
    
    def __init__(self, db_name: str, auth: dict, tables: list, timezone, logger: logging.Logger = logging):
        super().__init__(db_name, auth, tables, timezone=timezone)
        self.logger = logger
    
    async def new_user(self, user_id: UserId, role='Участник', mention=None, referal_id=None, 
                    reg_date=None, rating=None):
        if not reg_date:
            reg_date = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M')
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                cursor.execute('INSERT INTO users (user_id, mention, referal_id, reg_date, rating) VALUES '
                        + '(%s, %s, %s, %s, %s)', (user_id, mention, referal_id, reg_date, rating))

    async def delete_user(self, user_id):
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))

    async def take_all_users(self):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute('SELECT * FROM users')
                return cursor.fetchall()
        
    async def take_user(self, column: str, value):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute(f'SELECT * FROM users WHERE {column} = %s', (value,))
                return cursor.fetchone()

    async def change_ban_status_user(self, user_id, unbanned_date: datetime.datetime = None, unban: bool = False):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            if unbanned_date and unban:
                raise BaseException('Impossible action - Unban and ban at the same time')
            with connection:
                if not unbanned_date and not unban:
                    unbanned_date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')) + datetime.timedelta(days=50000)
                    cursor.execute(f'UPDATE users SET unbanned_date = %s WHERE user_id = %s', (unbanned_date, user_id))        
                elif unban:
                    unbanned_date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
                    cursor.execute(f'UPDATE users SET unbanned_date = %s WHERE user_id = %s', (unbanned_date, user_id))        
                else:
                    cursor.execute(f'UPDATE users SET unbanned_date = %s WHERE user_id = %s', (unbanned_date, user_id))        

    async def add_user_history(self, user_id, info):
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                cursor.execute('SELECT user_history FROM users WHERE user_id = %s', (user_id,))
                history = cursor.fetchone()
                try:
                    history = list(history[0])
                    history.append(info)
                except TypeError:
                    history = [info]
                history = json.dumps(history)
                cursor.execute('UPDATE users SET user_history = %s WHERE user_id = %s', (history, user_id))
