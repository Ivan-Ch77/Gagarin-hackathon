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
import memorycode.api as mc
from memorycode.config import (
    MEMORYCODE_EMAIL,
    MEMORYCODE_PASSWORD,
    MEMORYCODE_BASE_URL
)

import bot.kb as kb
from bot.callback import NameCallback
from bot.questions import QUESTIONS, FIELDS

class QuizScene(Scene, state="quiz"):

    @on.callback_query.enter()
    @on.message.enter()
    async def on_enter(self, msg: Message | CallbackQuery, state: FSMContext, step: int | None = 0) -> Any:

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
            # In case when the user tries to go back from the first question,
            # we just exit the quiz
            return await self.wizard.exit()
        return await self.wizard.back(step=previous_step)

    @on.callback_query(F.data == "cancel")
    async def cancel(self, clbck: CallbackQuery, state: FSMContext) -> None:
        await clbck.message.answer(text="Отмена заполнения")
        return await self.wizard.exit()

    @on.callback_query(F.data == "ask_submit")
    async def submit(self, clbck: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        print("Test")
        answers = data.get("answers", {})
        steps = data["step"]
        text = "<b>Проверьте основные данные</b>\n"+\
        f"<b>{FIELDS[0].text}</b> {answers[0]}\n"+\
        f"<b>{FIELDS[1].text}</b> {answers[1]}\n"+\
        f"<b>{FIELDS[2].text}</b> {answers[2]}"
        await clbck.message.answer(text=text)
        await self.wizard.exit()

    @on.callback_query.exit()
    @on.message.exit()
    async def exit(self, msg: Message | CallbackQuery, state: FSMContext) -> None:            
        await state.set_data({})

quiz_router = Router(name=__name__)
quiz_router.callback_query.register(QuizScene.as_handler(), NameCallback.filter(F.data == ("create_card", "back", "cancel", "ask_submit")))
quiz_router.message.register(QuizScene.as_handler(), Command("test"))
