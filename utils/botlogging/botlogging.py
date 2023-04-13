import json
import logging
import logging.config
import os
import sys

from config import config

from . import telegram_errors_handler

LOGGING_FILE = config.program.logs_file

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(processName)-10s - %(name)-10s "
            "- %(levelname)s - %(message)-10s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(message)s"},
    },
    "handlers": {
        "logfile": {
            "formatter": "default",
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_FILE,
            "maxBytes": 10485760,
            "backupCount": 5,
        },
        "verbose_output": {
            "formatter": "default",
            "level": config.program.logs_console_level,
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "telegram_handler": {
            "formatter": "default",
            "level": "ERROR",
            "class": "utils.botlogging.telegram_errors_handler.TelegramHandler",
            "bot_token": config.program.logs_token,
            "admin_id": config.program.logs_telegram_id,
            "bot_name": config.tg_bot.bot_name,
        },
    },
    "loggers": {
        "telegram_bot": {
            "level": "DEBUG",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "logfile",
            "verbose_output",
            "telegram_handler",
        ],
    },
}


def create_logs_folder():
    if not os.path.exists("logs"):
        os.mkdir("logs")


def prepare_logging():
    create_logs_folder()
    logging.config.dictConfig(LOGGING_CONFIG)
