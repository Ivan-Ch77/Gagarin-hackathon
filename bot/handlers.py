import logging
import json
from aiogram import types, F, Router
from aiogram.types import (
    KeyboardButton,
    Message, 
    CallbackQuery,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 


)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import delete_message, edit_message_text
from aiogram import Bot
from aiogram.fsm.scene import Scene, SceneRegistry, ScenesManager

from bot.state import *
from bot.callback import *
import bot.kb as kb
from bot.text import Text

from yandex.main import yandexGPT

from memorycode.api import MemoryCodeAPI as mc
from memorycode.config import (
    MEMORYCODE_EMAIL,
    MEMORYCODE_PASSWORD,
    MEMORYCODE_BASE_URL
)

router = Router()
text = Text()

#Обработчик команды старт
@router.message(Command("start"))
async def start_command(msg: Message, scenes: ScenesManager):
    await scenes.close()
    # if msg.from_user.id not in bd: - проверка наличия юзера в бд
    #     await msg.answer(text.new_start)
    await msg.answer(text.start, reply_markup=kb.menu)

@router.callback_query(F.data == "menu")
async def start_command(clbck: CallbackQuery, scenes: ScenesManager):
    await clbck.message.edit_text(text.start, reply_markup=kb.menu)

@router.callback_query(F.data == "edit_card")
async def edit_card(clbck: CallbackQuery):
    await clbck.message.edit_text(
        text="Выберите данные для обновления",
        reply_markup=kb.edit_data
    )

@router.callback_query(F.data == "create_card")
async def edit_card(clbck: CallbackQuery):
    await clbck.message.edit_text(
        text="Создание карточек доступно только для платных пользователей",
        reply_markup=kb.back_to_menu_kb
    )


#Обработчик кнопки "Редактировать карточку"
@router.callback_query(F.data == "epitaph")
@router.callback_query(F.data == "biography")
async def edit_card(clbck: CallbackQuery):
    try:
        api = mc(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL)
        # Аутентификация и получение токена доступа
        access_token = await api.authenticate()
        if access_token:
            pages_info = await api.get_all_memory_pages()
            text_ = text.edit
            name_ids = {}
            for page in pages_info:
                id = page['id']
                name = page['name']
                name_ids[id]=name
            await clbck.message.edit_text(
                text=text_,
                reply_markup=kb.page_kb(
                    edit_data=clbck.data,
                    name_ids=name_ids
                )
                
            )
        else:
            await clbck.answer(
                text="Вы не зарегистрированы",
            )
    except Exception as e:
        logging.warning(f'Error in start:\n{e}')


















# @router.message(UpdateInfo.epitaph_11)
# async def epitaph_11(msg: Message, state: FSMContext):
#     # await state.set_state(UpdateInfo.epitaph_show)
#     message = msg.text
#     await state.update_data(epitaph_11=message)
#     data = await state.get_data()
#     del data['msgID'], data['chatID']
#     user_answer = [value for value in data.values()]
#     print(user_answer)
#     ya_answer = await yandexGPT(user_answer)
#     print(ya_answer)
#     await state.update_data(ya_answer=ya_answer)
#     ya_answer = '\n'.join(ya_answer)
#     await msg.answer(
#         text=ya_answer+ "\nВыберите какой вариант вам больше понравился:",
#         reply_markup=kb.choise_answer
#     )
#     await state.set_state(UpdateInfo.epitaph_choice)

# @router.callback_query(UpdateInfo.epitaph_choice)
# async def epitaph_choice(clbck: CallbackQuery, state: FSMContext):
    
#     choice = clbck.data
#     await clbck.message.answer(
#         text= f'Выбран {choice}'
#     )

