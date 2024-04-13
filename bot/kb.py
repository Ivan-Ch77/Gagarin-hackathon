from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.callback import *


# кнопки для подтверждения информации в #забыл#
check_ready_answer_kb = [
    [ 
        InlineKeyboardButton(text="Оставить", callback_data="yes"),
        InlineKeyboardButton(text="Поменять", callback_data="no"),
    ],
    [ 
        InlineKeyboardButton(text="Назад", callback_data="back"),
    ],
    [
        InlineKeyboardButton(text="Закончить", callback_data="cancel"),
    ],
]
check_ready_answer_kb = InlineKeyboardMarkup(inline_keyboard=check_ready_answer_kb)

# кнопки для изменения ответа от яндекса
yandex_query = [
    [ 
        InlineKeyboardButton(text="Перегенирировать", callback_data="regenerate"),
        InlineKeyboardButton(text="Сохранить", callback_data="save"),
    ],
    [
        InlineKeyboardButton(text="Отмена", callback_data="cancel"),
    ]
]
yandex_query = InlineKeyboardMarkup(inline_keyboard=yandex_query)

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


back_to_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="В меню", callback_data="menu")]]
)

# выбор редактируемых данных
edit_data = [
    [ 
        InlineKeyboardButton(text="Эпитафия", callback_data="epitaph"),
        InlineKeyboardButton(text="Биография", callback_data="biography"),
    ]
]
edit_data = InlineKeyboardMarkup(inline_keyboard=edit_data)

# клавиатура для вопросов
necessary_q = [
    [
        InlineKeyboardButton(text="Назад", callback_data="back"),
    ],
    [
        InlineKeyboardButton(text="Закончить", callback_data="cancel"),
    ],
]
necessary_q = InlineKeyboardMarkup(inline_keyboard=necessary_q)


# клавиатура необязательных вопросов
unnecessary_q = [
    [
        InlineKeyboardButton(text="Назад", callback_data="back"),
    ],
    [
        InlineKeyboardButton(text="Готово", callback_data="ask_submit"),
    ],
]
unnecessary_q = InlineKeyboardMarkup(inline_keyboard=unnecessary_q)

# клавиатура для выбора ответов
choise_answer = [
    [
        InlineKeyboardButton(text="1", callback_data="1"),
        InlineKeyboardButton(text="2", callback_data="2"),
        InlineKeyboardButton(text="3", callback_data="3")
    ]
]
choise_answer = InlineKeyboardMarkup(inline_keyboard=choise_answer)



def page_kb(edit_data:str, name_ids:dict):
    builder = InlineKeyboardBuilder()

    for id, name in name_ids.items():
        if not name:
            name='Нет имени'
        builder.button(
            text=name,
            callback_data=NameCallback(
                tag="page_choose",
                edit_data=str(edit_data),
                id=str(id)
            )
        )
    builder.adjust(1, repeat=True)
    return builder.as_markup()
