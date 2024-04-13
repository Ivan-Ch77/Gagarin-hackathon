from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callback import *

# начальное меню бота
menu = [
    [ 
        InlineKeyboardButton(text="Новая карточка", callback_data="create_card"),
    ],
    [
        InlineKeyboardButton(text="Редактировать карточку", callback_data="edit_card"),
    ]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)



# клавиатура необязательных вопросов
unnecessary_q = [
    [
        InlineKeyboardButton(text="Пропустить", callback_data="skip"),
        InlineKeyboardButton(text="Закончить", callback_data="cancel"),
    ],
]
skip_question = InlineKeyboardMarkup(inline_keyboard=skip_question)

# клавиатура для выбора ответов
choise_answer = [
    [
        InlineKeyboardButton(text="1", callback_data="1"),
        InlineKeyboardButton(text="2", callback_data="2"),
        InlineKeyboardButton(text="3", callback_data="3")
    ]
]
choise_answer = InlineKeyboardMarkup(inline_keyboard=choise_answer)



def country_kb(name_ids:dict):
    builder = InlineKeyboardBuilder()

    for id, name in name_ids.items():
        builder.button(
            text=name,
            callback_data=NameCallback(
                tag="page_choose",
                id=str(id)
            )
        )
    builder.adjust(1, repeat=True)
    return builder.as_markup()