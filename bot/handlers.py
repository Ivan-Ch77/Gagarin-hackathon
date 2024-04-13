import logging
import json
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
from bot.text import Text

from yandex.main import yandexGPT

import memorycode.api as mc
from memorycode.config import (
    MEMORYCODE_EMAIL,
    MEMORYCODE_PASSWORD,
    MEMORYCODE_BASE_URL
)

router = Router()
text = Text()

@router.message(Command("start"))
async def start_command(msg: Message):
    # if msg.from_user.id not in bd:
    #     await msg.answer(text.new_start)
    await msg.answer(text.start, reply_markup=kb.menu)

@router.callback_query(F.data == "edit_card")
async def edit_card(clbck: CallbackQuery):
    try:
        access_token = await mc.get_access_token(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD)
        if access_token:
            pages_info = await mc.get_all_memory_pages(access_token)
            text_ = text.edit
            name_ids = {}
            for page in pages_info:
                id = page['id']
                name = page['name']
                name_ids[id]=name
            await clbck.message.edit_text(
                text=text_,
                reply_markup=kb.country_kb(name_ids)
            )
        else:
            await clbck.answer(
                text="Вы не зарегестрированы",
            )
    except Exception as e:
        logging.warning(f'Error in start:\n{e}')


# @router.callback_query(NameCallback.filter(F.tag == "page_choose"))
# async def update_info(clbck: CallbackQuery, state: FSMContext, callback_data: NameCallback):
#     access_token = await mc.get_access_token(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD)
#     select_id = callback_data.id
#     if access_token:
#         pages_info = await mc.get_all_memory_pages(access_token)
#         page_info = ''
#         for page in pages_info:
#             if str(page['id']) == select_id:
#                 page_info = page
#                 break
#         print(json.dumps(page_info, indent=2, ensure_ascii=False))
    
#     text_ = text.epitaph_text()['text']
#     await clbck.message.edit_text(
#         text=text_,
#     )

#     if not page_info['name']:
#         await state.set_state(UpdateInfo.epitaph_1)
#         await state.update_data(
#             page_info=page_info,
#             msgID=clbck.message.message_id,
#             chatID=clbck.message.chat.id
#         )
#         question = text.epitaph_text()['question'][0]
#         await clbck.message.answer(
#             text=question,
#             reply_markup=kb.skip_question
#         )
        
#     else:
#         await state.set_state(UpdateInfo.epitaph_2)
#         await state.update_data(
#             page_info=page_info,
#             msgID=clbck.message.message_id,
#             chatID=clbck.message.chat.id,
#             epitaph_1=page_info['name']
#         )
#         question = text.epitaph_text()['question'][1]
#         await clbck.message.answer(
#             text=question,
#             reply_markup=kb.skip_question
#         )
    

@router.message(UpdateInfo.epitaph_11)
async def epitaph_11(msg: Message, state: FSMContext):
    # await state.set_state(UpdateInfo.epitaph_show)
    message = msg.text
    await state.update_data(epitaph_11=message)
    data = await state.get_data()
    del data['msgID'], data['chatID']
    user_answer = [value for value in data.values()]
    print(user_answer)
    ya_answer = await yandexGPT(user_answer)
    print(ya_answer)
    await state.update_data(ya_answer=ya_answer)
    ya_answer = '\n'.join(ya_answer)
    await msg.answer(
        text=ya_answer+ "\nВыберите какой вариант вам больше понравился:",
        reply_markup=kb.choise_answer
    )
    await state.set_state(UpdateInfo.epitaph_choice)

@router.callback_query(UpdateInfo.epitaph_choice)
async def epitaph_choice(clbck: CallbackQuery, state: FSMContext):
    
    choice = clbck.data
    await clbck.message.answer(
        text= f'Выбран {choice}'
    )

