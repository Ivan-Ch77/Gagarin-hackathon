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
from bot.text import Text


router = Router()
text = Text()


@router.message(Command("start"))
async def start_command(msg: Message):
    try:
        text_ = text.start() 
        await msg.answer(
            text=text_,
            reply_markup=kb.menu
        )
    except Exception as e:
        logging.warning(f'Error in start:\n{e}')
        

@router.callback_query(F.data == "create")
async def create(clbck: CallbackQuery):
    ...
    
    
@router.callback_query(F.data == "support")
async def support(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Support.biography_intro_1)

    text_ = text.base_info()
    await clbck.message.edit_text(
        text="Давайте напишем биографию вместе, начнем с вступления ответте на пару вопросов",
    )
    await state.update_data(msgID=clbck.message.message_id,
                            chatID=clbck.message.chat.id)
    await clbck.message.answer(
        text="QW1:",
        reply_markup=kb.skip_question
    )
    
    
@router.message(Support.biography_intro_1)
async def biography_intro_1(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_2)
    message = msg.text
    await state.update_data(biography_intro_1=message)
    await msg.answer(
        text="QW2:",
        reply_markup=kb.skip_question
    )
    
    
@router.message(Support.biography_intro_2)
async def biography_intro_2(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_3)
    message = msg.text
    await state.update_data(biography_intro_2=message)
    await msg.answer(
        text="QW3:",
        reply_markup=kb.skip_question
    )
    
    
@router.message(Support.biography_intro_3)
async def biography_intro_3(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_show)
    message = msg.text
    await state.update_data(biography_intro_3=message)
    data = await state.get_data()
    await msg.answer(
        text=f'{data}'+ "\nОставляем:",
        reply_markup=kb.check_kb
    )


# @router.message(Support.biography_intro_show)
# async def biography_intro_show(msg: Message, state: FSMContext):
    
    
#     # await state.set_state(Support.biography_intro_show)
