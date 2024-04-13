import asyncio
import json
import logging
from datetime import datetime, timedelta
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
from yandex.main import yandexGPT

text = Text()



#Сцена 1 - для обработки эпитафий
class EpitaphUpdateScene(Scene, state="update"):

    #Обработчик для редактирования пользователей
    # @on.callback_query.enter(NameCallback.filter())
    
    # async def __init__(self, data: NameCallback, bot: Bot, state: FSMContext, step: int | None = 0, **kwargs):
        # clbck_data_id = NameCallback.unpack(data.data).id
        # api = mc(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL)
        # access_token = await api.authenticate()
        
        
        #--------------------Тут просто взять данные из словаря---------------------

    async def get_api(self, state: FSMContext, user_id):
        data = await state.get_data()
        api = data.get('api')
        if not api:
            api = mc(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL)
            api.access_token = await api.authenticate()
            await state.update_data(api=api)
        return api

    @on.callback_query.enter()
    @on.message.enter()
    async def on_enter(
        self, 
        msg: CallbackQuery | Message, 
        state: FSMContext,
        step: int | None = 0
    ) -> Any:

        user_id = msg.from_user.id
        api = await self.get_api(state, user_id)

        if not step: # На самом первом шаге обрабатывается CallbackQuery на остальных Message
            clbck_data_id = NameCallback.unpack(msg.data).id
            if api.access_token:
                pages = await api.get_all_memory_pages()
                select_page = next((page for page in pages if str(clbck_data_id) == str(page['id'])), None)
                if select_page:
                    await state.update_data(select_page=select_page)

        if type(msg) == CallbackQuery:
            msg = msg.message


        try: # Остановка сцены когда заканчиваются вопросы
            question = QUESTIONS[step]
        except IndexError:
            data = await state.get_data()
            select_page = data['select_page']
            answers = data['answers']
            user_answers = [value for value in answers.values()]
            ya_answer = await yandexGPT(user_answers)
            if type(ya_answer) == list:
                ya_answer = ya_answer[0]
            await msg.answer(
                text = ya_answer,
                # reply_markup=kb.choise_answer
            )
            if api.access_token:
                updated_fields = {'epitaph': ya_answer}
                updated_page = await api.update_memory_page(json.dumps(select_page), json.dumps(updated_fields))
            return await self.wizard.exit()

        # Пропуск вопросов на которые уже есть ответы
        await state.update_data(step=step)
        
        data = await state.get_data()
        page = data['select_page']
        if question.answer:
            key = question.answer.key
            tmp_availiable = True
        else: 
            key = None
            tmp_availiable = False

        if type(key) ==  list:
            for elem in key:
                if not page[elem]:
                    tmp_availiable = False
                    break
            # пришлось хардкодить хз как автоматизировать
            if tmp_availiable:
                if "birthday_at" in key and "died_at" in key:
                    birth_i = key.index("birthday_at")
                    death_i = key.index("died_at")
                    birthday = datetime.strptime(page[key[birth_i]], "%Y-%m-%d %H:%M:%S")
                    deathday = datetime.strptime(page[key[death_i]], "%Y-%m-%d %H:%M:%S")
                    year_life = (deathday - birthday).days // 365
                    question.answer.text = str(year_life)
                
        elif type(key) == str:
            
            if page[key]:
                question.answer.text = page[key]
            else:
                tmp_availiable = False

        if tmp_availiable:
            text_ = question.text            
            answers = data.get("answers", {})
            answers[step] = question.answer.text
            await state.update_data(answers=answers, allow_msg=False)
            
            return await msg.answer(
                text = 'На вопрос "' + text_ + f'" уже есть ответ:\n<b>{question.answer.text}</b>\nОставить его?',
                reply_markup=kb.check_kb,
            )
        else:
            await state.update_data(allow_msg=True)
            text_ = question.text
            return await msg.answer(
                text = text_,
                reply_markup=kb.necessary_q,
            )

        # if step < 3:
        #     return await msg.answer(
        #         text = text_,
        #         reply_markup=kb.necessary_q,
        #     )
        # else:         
        #     return await msg.answer(
        #         text = text_,
        #         reply_markup=kb.unnecessary_q,
        #     )



    @on.message(F.text)
    async def answer(self, msg: Message, state: FSMContext) -> None:
        data = await state.get_data()
        allow_msg = data['allow_msg']
        if allow_msg:
            step = data["step"]
            answers = data.get("answers", {})
            answers[step] = msg.text
            print(data)
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
    
    # Выбор существующего ответа
    @on.callback_query(F.data == "yes")
    async def stay_answer(self, clbck: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        step = data['step']
        await self.wizard.retake(step=step + 1)

    @on.callback_query(F.data == "no")
    async def edit_answer(self, clbck: CallbackQuery, state: FSMContext) -> None:
        await state.update_data(allow_msg=True)
        data = await state.get_data()
        step = data['step']
        await clbck.message.answer(text="Напишите желаемый ответ")
    
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

update_router = Router(name=__name__)
update_router.callback_query.register(
    EpitaphUpdateScene.as_handler(), 
    NameCallback.filter(F.tag == "page_choose")
)




#Сцена 2 - для обработки эпитафии и биографии
class AboutScene(Scene, state="about"):
    ...

about_router = Router(name=__name__)
about_router.callback_query.register(AboutScene.as_handler(), NameCallback.filter("DATA"))
about_router.message.register(AboutScene.as_handler(), Command("COMMAND"))
