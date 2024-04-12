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

choise_answer = [
    [
        InlineKeyboardButton(text="1", callback_data="1"),
        InlineKeyboardButton(text="2", callback_data="2"),
        InlineKeyboardButton(text="3", callback_data="3")
    ]
]
choise_answer = InlineKeyboardMarkup(inline_keyboard=choise_answer)