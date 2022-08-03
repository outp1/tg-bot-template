from datetime import datetime

import pytz
from psycopg2 import extras

from .pgsqlighter import DatabaseConnection

# Database Class example
class UserTables(DatabaseConnection): 
    
    def __init__(self, db_name: str, auth: dict, tables: list):
        super().__init__(db_name, auth, tables)
    
    async def new_user(self, user_id, mention=None, referal_id=None, rating=None):
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                cursor.execute('INSERT INTO users (user_id, mention, referal_id, reg_date, rating) VALUES '
                        + '(%s, %s, %s, NOW(), %s)', (user_id, mention, referal_id, rating))

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

    async def ban_user(self, user, unbanned_date: datetime = None):
        with self.sqlighter as connection:
            cursor = connection.cursor(cursor_factory=extras.DictCursor)
            with connection:
                cursor.execute(f'UPDATE users SET unbanned_date = %s WHERE user = %s', (unbanned_date, user))        
