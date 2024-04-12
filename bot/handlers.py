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

    text_ = text.biography_intro()['text']
    await clbck.message.edit_text(
        text=text_,
    )
    await state.update_data(msgID=clbck.message.message_id,
                            chatID=clbck.message.chat.id)
    question = text.biography_intro()['question'][0]
    await clbck.message.answer(
        text=question,
        reply_markup=kb.skip_question
    )
    
    
@router.message(Support.biography_intro_1)
async def biography_intro_1(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_2)
    message = msg.text
    await state.update_data(biography_intro_1=message)
    question = text.biography_intro()['question'][1]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )
    
    
@router.message(Support.biography_intro_2)
async def biography_intro_2(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_3)
    message = msg.text
    await state.update_data(biography_intro_2=message)
    question = text.biography_intro()['question'][2]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )

@router.message(Support.biography_intro_3)
async def biography_intro_3(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_4)
    message = msg.text
    await state.update_data(biography_intro_3=message)
    question = text.biography_intro()['question'][3]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )

@router.message(Support.biography_intro_4)
async def biography_intro_4(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_5)
    message = msg.text
    await state.update_data(biography_intro_4=message)
    question = text.biography_intro()['question'][4]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )

@router.message(Support.biography_intro_5)
async def biography_intro_5(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_6)
    message = msg.text
    await state.update_data(biography_intro_5=message)
    question = text.biography_intro()['question'][5]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )
    
@router.message(Support.biography_intro_6)
async def biography_intro_6(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_7)
    message = msg.text
    await state.update_data(biography_intro_6=message)
    question = text.biography_intro()['question'][6]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )

@router.message(Support.biography_intro_7)
async def biography_intro_7(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_8)
    message = msg.text
    await state.update_data(biography_intro_7=message)
    question = text.biography_intro()['question'][7]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )
    
@router.message(Support.biography_intro_8)
async def biography_intro_8(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_9)
    message = msg.text
    await state.update_data(biography_intro_8=message)
    question = text.biography_intro()['question'][8]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )
        
@router.message(Support.biography_intro_9)
async def biography_intro_9(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_10)
    message = msg.text
    await state.update_data(biography_intro_9=message)
    question = text.biography_intro()['question'][9]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )

@router.message(Support.biography_intro_10)
async def biography_intro_10(msg: Message, state: FSMContext):
    await state.set_state(Support.biography_intro_11)
    message = msg.text
    await state.update_data(biography_intro_10=message)
    question = text.biography_intro()['question'][10]
    await msg.answer(
        text=question,
        reply_markup=kb.skip_question
    )

@router.message(Support.biography_intro_11)
async def biography_intro_11(msg: Message, state: FSMContext):
    # await state.set_state(Support.biography_intro_show)
    message = msg.text
    await state.update_data(biography_intro_11=message)
    data = await state.get_data()
    del data['msgID'], data['chatID']
    answer__list = [value for value in data.values()]
    await msg.answer(
        text=f'{data}'+ "\nВыберите какой вариант вам больше понравился:",
        reply_markup=kb.choise_answer
    )
    await state.set_state(Support.biography_intro_choice)

@router.callback_query(Support.biography_intro_choice)
async def biography_intro_choice(clbck: CallbackQuery, state: FSMContext):
    
    choice = clbck.data
    await clbck.message.answer(
        text= f'Выбран {choice}'
    )

# @router.message(Support.biography_intro_show)
# async def biography_intro_show(msg: Message, state: FSMContext):
    
    
#     # await state.set_state(Support.biography_intro_show)
