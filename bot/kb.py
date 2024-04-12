from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callback import *

# начальное меню бота
menu = [
    [
        InlineKeyboardButton(text="Создание", callback_data="create"),
        InlineKeyboardButton(text="Помощь", callback_data="support"),
    ],
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)

# клавиатура для пропуска вопроса
skip_question = [
    [
        InlineKeyboardButton(text="Пропустить", callback_data="skip"),
        InlineKeyboardButton(text="Закончить", callback_data="cancel"),
    ],
]
skip_question = InlineKeyboardMarkup(inline_keyboard=skip_question)

check_kb = [
    [
        InlineKeyboardButton(text="Да", callback_data="Yes"),
        InlineKeyboardButton(text="Нет", callback_data="No")
    ]
]
check_kb = InlineKeyboardMarkup(inline_keyboard=check_kb)