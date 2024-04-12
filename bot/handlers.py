import logging
from aiogram import types, F, Router
from aiogram.types import (
    KeyboardButton,
    Message, 
    CallbackQuery,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import delete_message, edit_message_text
from aiogram import Bot

from bot.state import *
from bot.callback import *
import bot.kb as kb
import bot.text as text


router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    try:
        await msg.answer(
            text='Hellow',
            reply_markup=kb.menu
        )
    except Exception as e:
        logging.warning(f'Error in start:\n{e}')