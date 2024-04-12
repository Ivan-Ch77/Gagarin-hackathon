from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callback import *

menu = [
    [
        InlineKeyboardButton(text="Начать", callback_data="start"),
    ],
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)