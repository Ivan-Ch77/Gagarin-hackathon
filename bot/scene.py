import asyncio
import json
import logging
from os import getenv
from typing import Any

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, SceneRegistry, ScenesManager, on

from aiogram.types import KeyboardButton, Message, ReplyKeyboardRemove, CallbackQuery

from aiogram.utils.formatting import (
    Bold,
    as_key_value,
    as_list,
    as_numbered_list,
    as_section,
)
from memorycode.api import MemoryCodeAPI as mc
from memorycode.config import (
    MEMORYCODE_EMAIL,
    MEMORYCODE_PASSWORD,
    MEMORYCODE_BASE_URL
)
from aiogram.filters.callback_data import CallbackData
import bot.kb as kb
from bot.callback import NameCallback
from bot.questions import QUESTIONS, FIELDS
from bot.text import Text

text = Text()

#Сцена 1 - для обработки простых вопросов
class QuizScene(Scene, state="quiz"):

    #Обработчик для редактирования пользователей
    @on.callback_query.enter(NameCallback.filter())
    async def enter_edit_card(self, data: NameCallback, bot: Bot, state: FSMContext, step: int | None = 0):
        chat_id = data.message.chat.id
        print(data.id)
        api = mc(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL)
        access_token = await api.authenticate()
        
        #--------------------Тут просто взять данные из словаря---------------------

    @on.message.enter()
    async def on_enter(self, msg: CallbackQuery | Message, state: FSMContext, step: int | None = 0) -> Any:
        #обрабатваем шаги начиная с 0. IndexError вызовется когда достигнем лимит вопросов
        try:
            quiz = QUESTIONS[step]
        except IndexError:
            return await self.wizard.exit()
        
        await state.update_data(step=step)

        text = QUESTIONS[step].text 
        
        if step < 3:
            return await msg.answer(
                text,
                reply_markup=kb.necessary_q,
            )
        else:         
            return await msg.answer(
                text,
                reply_markup=kb.unnecessary_q,
            )

    @on.message(F.text)
    async def answer(self, msg: Message, state: FSMContext) -> None:
        data = await state.get_data()
        step = data["step"]
        
        answers = data.get("answers", {})
        answers[step] = msg.text
        
        await state.update_data(answers=answers)

        await self.wizard.retake(step=step + 1)

    @on.callback_query(F.data == "back")
    async def back(self, clbck: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        step = data["step"]
        previous_step = step - 1
        if previous_step < 0:
            clbck.message.answer(text="Отмена заполнения")
            return await self.wizard.exit()
        return await self.wizard.back(step=previous_step)

    #Обработка кнопки отменить
    @on.callback_query(F.data == "cancel")
    async def cancel(self, clbck: CallbackQuery, state: FSMContext) -> None:
        await clbck.message.answer(text="Отмена заполнения")
        return await self.wizard.exit()

    #Обработка сабмита
    @on.callback_query(F.data == "ask_submit")
    async def submit(self, clbck: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        print("Test")
        answers = data.get("answers", {})
        steps = data["step"]
        text = "Проверьте основные данные\n"+\
        f"<b>{FIELDS[0].text}</b> {answers[0]}\n"+\
        f"<b>{FIELDS[1].text}</b> {answers[1]}\n"+\
        f"<b>{FIELDS[2].text}</b> {answers[2]}"
        await clbck.message.answer(text=text)
        await self.wizard.exit()

    #Обработка выхода
    @on.callback_query.exit()
    @on.message.exit()
    async def exit(self, msg: Message | CallbackQuery, state: FSMContext) -> None:            
        await state.set_data({})

quiz_router = Router(name=__name__)
quiz_router.callback_query.register(QuizScene.as_handler(), NameCallback.filter(F.tag == "page_choose"))
quiz_router.message.register(QuizScene.as_handler(), Command("test"))



#Сцена 2 - для обработки эпитафии и биографии
class AboutScene(Scene, state="about"):
    ...

about_router = Router(name=__name__)
about_router.callback_query.register(AboutScene.as_handler(), NameCallback.filter("DATA"))
about_router.message.register(AboutScene.as_handler(), Command("COMMAND"))
