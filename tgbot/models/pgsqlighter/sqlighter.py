import psycopg2
import datetime
import pytz
from tgbot.config import Config


class Sqlighter:
    def __init__(self, db_name: str, auth: dict):
        self.db_name = db_name
        self.auth = auth

    def __enter__(self):
        self.connection = psycopg2.connect(
            user=self.auth["user"],
            # пароль, который указали при установке PostgreSQL
            password=self.auth["password"],
            host=self.auth["host"],
            port=self.auth["port"],
            database=self.db_name,
        )
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        if exc_val:
            raise


class DatabaseConnection(Sqlighter):
    def __init__(
        self,
        db_name: str,
        auth: dict,
        tables: list = None,
        timezone: pytz.tzinfo.tzinfo = pytz.timezone("Europe/Moscow"),
    ):
        self.db_name = db_name
        self.sqlighter = Sqlighter(self.db_name, auth)
        self.tables = tables
        self.timezone = timezone
        if self.tables:
            self.create_tables()
            self.set_timezone()

    def create_tables(self):
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                status = cursor.execute("".join(self.tables))

    def set_timezone(self):
        with self.sqlighter as connection:
            cursor = connection.cursor()
            with connection:
                cursor.execute(f"SET TIME ZONE '{self.timezone}';")
