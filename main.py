
import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.scene import Scene, SceneRegistry

from bot.handlers import router
from bot.scene import QuizScene, quiz_router

load_dotenv()
API_KEY = os.getenv('API_KEY_TG')


async def main():
    bot = Bot(API_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage(),events_isolation=SimpleEventIsolation(),)
    dp.include_router(router)
    dp.include_router(quiz_router)
    scene_registry = SceneRegistry(dp)
    scene_registry.add(QuizScene)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.error('KeyboardInterrupt')

