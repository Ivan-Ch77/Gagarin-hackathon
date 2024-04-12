import logging
from aiogram import Bot, Dispatcher, executor
from bot.config import API_KEY_TG
from bot.handlers import register_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_KEY_TG)
dp = Dispatcher(bot)

register_handlers(dp)

async def on_startup(dispatcher):
    logger.info("Бот запущен!")

async def on_shutdown(dispatcher):
    logger.info("Бот останавливается...")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
