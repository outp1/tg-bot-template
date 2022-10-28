from datetime import datetime
import pytz

from .pgsqlighter import DatabaseConnection

# Database table class example
class UserTables(DatabaseConnection): 
    
    def __init__(self, db_name: str, auth: dict, tables: list):
        super().__init__(db_name, auth, tables)
    
    async def new_user(self, user_id, mention=None, referal_id=None, 
                    reg_date=None, rating=None):
        if not reg_date:
            reg_date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M')
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                cursor.execute('INSERT INTO users (user_id, mention, referal_id, reg_date, rating) VALUES '
                        + '(%s, %s, %s, %s, %s)', (user_id, mention, referal_id, reg_date, rating))


