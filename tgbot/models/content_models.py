from datetime import datetime
import pytz

from .pgsqlighter import DatabaseConnection


# Tables containing content for some posts
class ContentTables(DatabaseConnection):

    def __init__(self, db_name: str, auth: dict, tables: list, default_contents: list = None):
        super().__init__(db_name, auth, tables)
        self.default_contents = default_contents
        if self.default_contents:
            self.insert_message_default_content()
    
    def insert_message_default_content(self):
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                cursor.execute('SELECT * FROM content')
                if not cursor.fetchall():
                    for c in self.default_contents:
                        cursor.execute(
                                'INSERT INTO content (key, text, media_type, media) VALUES (%s, %s, %s, %s)',
                                (c[0], c[1], c[2], c[3]))
        
    async def take_message_content(self, key: str):
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                cursor.execute('SELECT * FROM content WHERE key = %s', (key,))
                return cursor.fetchone()


        
        


