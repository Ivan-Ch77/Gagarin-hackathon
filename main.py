
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
from bot.scene import QuizScene, AboutScene, quiz_router, about_router

load_dotenv()
API_KEY = os.getenv('API_KEY_TG')

def create_dispatcher():

    dispatcher = Dispatcher(
        storage=MemoryStorage(),
        events_isolation=SimpleEventIsolation(),
    )

    #Включаем в диспетчер все роутеры
    dispatcher.include_router(quiz_router)
    dispatcher.include_router(about_router)
    dispatcher.include_router(router)

    scene_registry = SceneRegistry(dispatcher)

    scene_registry.add(QuizScene)
    scene_registry.add(AboutScene)


    return dispatcher

async def main():
    bot = Bot(API_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = create_dispatcher()

    #drop_pending_updates поменял на None, потому что иначе на команду /start бот не отзывается с первого раза
    await bot.delete_webhook(drop_pending_updates=None) 
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.error('KeyboardInterrupt')

