import asyncio
import json
import logging
from dataclasses import dataclass, field
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

from bot.callback import NameCallback

    
@dataclass
class Question:

    text: str


QUESTIONS = [
    Question(
        text="Как его звали?"
    ),
    Question(
        text="Сколько лет ему было, когда он ушел от нас?"
    ),
    Question(
        text="В какой стране и городе он родился?"
    ),
    Question(
        text="Какую профессию он имел?"
    ),
    Question(
        text="Что он любил делать в свободное время?"
    ),
    Question(
        text="Был ли он религиозным человеком?"
    ),
    Question(
        text="Имел ли он какие-то особые увлечения/хобби?"
    ),
    Question(
        text="Были ли у него особые жизненные принципы или ценности, которые он хотел бы передать своим потомкам?"
    ),
    Question(
        text="Был ли он хорошим семьянином?"
    ),
    Question(
        text="Каким он был по характеру: добрым, веселым, строгим, спокойным?"
    ),
    Question(
        text="Есть ли какие-то особенные истории или моменты, связанные с ним, которые ты хотел бы увековечить в эпитафии?"
    )
]


class QuizScene(Scene, state="quiz"):

    @on.callback_query.enter()
    @on.message.enter()
    async def on_enter(self, msg: CallbackQuery | Message, state: FSMContext, step: int | None = 0) -> Any:
        if not step:
            
            # access_token = await mc.get_access_token(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD)
            # select_id = NameCallback.id
            # print(select_id)
            # if access_token:
            #     pages_info = await mc.get_all_memory_pages(access_token)
            #     page_info = ''
            #     for page in pages_info:
            #         if str(page['id']) == select_id:
            #             page_info = page
            #             break
            #     print(json.dumps(page_info, indent=2, ensure_ascii=False))
            # else:
            #     return await self.wizard.exit()
            msg = msg.message
            await msg.answer("Давайте напишем биографию вместе, начнем с эпитафии ответьте на пару вопросов")    
        
        try:
            quiz = QUESTIONS[step]
        except IndexError:
            return await self.wizard.exit()
        
        await state.update_data(step=step)
        return await msg.answer(
            text=QUESTIONS[step].text
        )

    
    @on.message(F.text)
    async def answer(self, msg: Message, state: FSMContext) -> None:
        data = await state.get_data()
        step = data["step"]

        answers = data.get("answers", {})
        answers[step] = msg.text
        
        await state.update_data(answers=answers)
        print(data)
        
        await self.wizard.retake(step=step + 1)
        
    
quiz_router = Router(name=__name__)
quiz_router.callback_query.register(QuizScene.as_handler(), NameCallback.filter(F.tag == "page_choose"))