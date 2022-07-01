import json
import logging
import requests

class TelegramHandler(logging.Handler):

    def __init__(self, bot_token: str, admin_id: str, bot_name: str):
        self.bot_name = bot_name
        self.admin_id = admin_id
        self.url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        super().__init__(level=logging.ERROR)


    def emit(self, record: logging.LogRecord):
        logEntry = self.format(record)
        text = f"""
К тебе взывает робот <b>{self.bot_name}</b>:
<code>{logEntry}</code>
"""
        if type(self.admin_id) == list:
            for admin in self.admin_id:
                data = {
                    'text': text,
                    'chat_id': admin,
                    'parse_mode': 'HTML'
                }
                response = requests.post(self.url, data=data)
        else:
            data = {
                'text': text,
                'chat_id': self.admin_id,
                'parse_mode': 'HTML'
            }
            response = requests.post(self.url, data=data)

