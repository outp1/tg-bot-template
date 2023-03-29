import asyncio

from utils.botlogging import prepare_logging
from bot import setup_tgbot

prepare_logging()

if __name__ == "__main__":
    try:
        asyncio.run(setup_tgbot())
    except KeyboardInterrupt:
        pass
