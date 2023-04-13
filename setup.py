import asyncio

from bot import setup_tgbot
from utils.botlogging import prepare_logging

prepare_logging()

if __name__ == "__main__":
    try:
        asyncio.run(setup_tgbot())
    except KeyboardInterrupt:
        pass
