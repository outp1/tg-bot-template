import os
import sys
import logging
import json
import logging.config
from . import telegram_errors_handler

class BotLogging:

    # TODO: automatic tg handler in module detection 
    dir_path = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, logger_name: str, logs_dir: str, bot_token: str, admin: str, 
            bot_nickname: str = 'Bot', config_file: str = f'{dir_path}/loggers.json', template: str = 'default', 
            tg_handler_dir: str = None): 
        self.logs_dir = logs_dir
        self.logger_name = logger_name
        self.bot_token = bot_token
        self.admin = admin
        self.template = template
        self.config_file = config_file
        self.bot_nickname = bot_nickname
        self.tg_handler_dir = tg_handler_dir 

    def get_handler_dir(self, handler_dir: str): 
        path = self.dir_path.split('/')
        path = '.'.join(path)
        return path + handler_dir

    def create_logs_folder(self, logs_dir: str):
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)
    
    def get_bot_logger(self):
        self.create_logs_folder(self.logs_dir)
        with open(self.config_file, "r") as f:
            dict_config = json.load(f)
            if not dict_config["handlers"]["telegram"]: 
                return None
            dict_config["handlers"]["telegram"]["bot_token"] = self.bot_token 
            dict_config["handlers"]["telegram"]["admin_id"] = self.admin
            dict_config["handlers"]["telegram"]["bot_name"] = self.bot_nickname
            dict_config["handlers"]["telegram"]["class"] = self.tg_handler_dir.replace('/', '.') + '.TelegramHandler'
            dict_config["loggers"][self.logger_name] = dict_config["loggers"][self.template]
        logging.config.dictConfig(dict_config)
        return logging.getLogger(self.logger_name)
    
    def get_default_logger(self):
        create_logs_folder()
        with open(self.config_file, "r") as f:
            logging.config.dictConfig(json.load(f))
        return logging.getLogger("default")
    
    def get_logger(self):
        logger, status = self.get_bot_logger(), 'Telegram Bot'
        if not logger: 
            logger, status = self.get_default_logger(), 'Default'
        logger.info(f'Starting {self.logger_name} logger with handler {status}')
        return logger

