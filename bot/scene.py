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
from bot.questions import EPITAPH_QUESTIONS, FIELDS
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
        bot: Bot,
        state: FSMContext,
        step: int | None = 0
    ) -> Any:

        first_data = await state.get_data()
        if type(msg) == CallbackQuery:
            message = msg.message
        # На самом первом шаге обрабатывается CallbackQuery на остальных Message
        if not step and not first_data:
            clbck_data_id = NameCallback.unpack(msg.data).id
            api = await self.get_api(state, msg.from_user.id)
            if api.access_token:
                pages = await api.get_all_memory_pages()
                select_page = next((page for page in pages if str(clbck_data_id) == str(page['id'])), None)
                if select_page:
                    await state.update_data(select_page=select_page)
                    name = select_page['name']
                    if name:
                        page_msg = await message.edit_text(f"Выбрана карточка {name}")
                    else:
                        page_msg = await message.edit_text(f"Выбрана карточка без названия")
                    data = await state.update_data(
                        page_chat_id=page_msg.chat.id,
                        page_msg_id=page_msg.message_id
                    )

        # Остановка сцены когда заканчиваются вопросы
        try:
            question = EPITAPH_QUESTIONS[step]
        except IndexError:

            data = await state.get_data()
            await bot.edit_message_text(
                chat_id=data['chat_id'],
                message_id=data['msg_id'],
                text = "Создание эпитафии...",
            )
            select_page = data['select_page']
            answers = data['answers']
            user_answers = [value for value in answers.values()]
            ya_answer = await yandexGPT(user_answers)
            if type(ya_answer) == list:
                ya_answer = ya_answer[0]
            await bot.edit_message_text(
                chat_id=data['chat_id'],
                message_id=data['msg_id'],
                text = ya_answer,
                reply_markup=kb.yandex_query
            )
            data = await state.update_data(
                allow_msg=False,
                ya_answer=ya_answer
            )
            return

        # Пропуск вопросов на которые уже есть ответы (ВОПРОСЫ!!!)
        data = await state.update_data(step=step)

        # data = await state.get_data()
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

        # Проверка на наличие ключа типа str в EPITAPH_QUESTIONS
        elif type(key) == str:

            # Проверка есть ли key в EPITAPH_QUESTIONS
            if page[key]:
                question.answer.text = page[key]
            # Если нет
            else:
                tmp_availiable = False

        # print(data)
        # В EPITAPH_QUESTIONS key не существует
        if tmp_availiable:
            text_ = question.text
            print('ВЗЯТО ИЗ MC', text_)
            answers = data.get("answers", {})
            answers[step] = question.answer.text

            # Проверяем чтобы step == 0 and first_data is empty
            if not step and not first_data:
                # print('step', step)
                # print('first_data', first_data)
                message = await message.answer(
                    text = f"Вопрос {step+1}/{len(EPITAPH_QUESTIONS)}\n" + 'Для вопроса "' + text_ + f'" уже есть ответ:\n<b>{question.answer.text}</b>\nОставить его?',
                    reply_markup=kb.check_ready_answer_kb,
                )
            # Во всех случаях, когда step != 0 and first_data not empty
            else:
                print('step', step)
                print('first_data', first_data)
                message = await bot.edit_message_text(
                    chat_id=data['chat_id'],
                    message_id=data['msg_id'],
                    text = f"Вопрос {step+1}/{len(EPITAPH_QUESTIONS)}\n" + 'Для вопроса "' + text_ + f'" уже есть ответ:\n<b>{question.answer.text}</b>\nОставить его?',
                    reply_markup=kb.check_ready_answer_kb,
                )

            data = await state.update_data(
                answers=answers,
                allow_msg=False,
                chat_id=message.chat.id,
                msg_id=message.message_id
            )
        # Значение key в EPITAPH_QUESTIONS не существует
        else: # Нет данных для ответа на вопрос из MemoryCode
            text_ = question.text
            if not step and not first_data:
                message = await message.answer(
                    text = f"Вопрос {step+1}/{len(EPITAPH_QUESTIONS)}\n" + text_,
                    reply_markup=kb.necessary_q,
                )
            else:
                message = await bot.edit_message_text(
                    chat_id=data['chat_id'],
                    message_id=data['msg_id'],
                    text = f"Вопрос {step+1}/{len(EPITAPH_QUESTIONS)}\n" + text_,
                    reply_markup=kb.necessary_q,
                )
            data = await state.update_data(
                allow_msg=True,
                chat_id=message.chat.id,
                msg_id=message.message_id
            )

    # Ответы пользователя на вопросы
    @on.message(F.text)
    async def answer(self, msg: Message, bot: Bot, state: FSMContext) -> None:
        data = await state.get_data()
        allow_msg = data['allow_msg']
        if allow_msg:
            step = data["step"]

            answers = data.get("answers", {})
            answers[step] = msg.text
            await state.update_data(answers=answers)
            await msg.delete()
            try:
                change_field_msg_id = data['change_field_msg_id']
                change_field_chat_id = data['change_field_chat_id']
                await bot.delete_message(chat_id=change_field_chat_id, message_id=change_field_msg_id)
            except Exception as e:
                pass
            await self.wizard.retake(step=step + 1)


    @on.callback_query(F.data == "back")
    async def back(self, clbck: CallbackQuery, bot: Bot, state: FSMContext) -> None:
        data = await state.get_data()
        step = data["step"]
        previous_step = step - 1
        if previous_step < 0:
            await bot.delete_message(chat_id=data['page_chat_id'], message_id=data['page_msg_id'])
            await bot.edit_message_text(
                chat_id=data['chat_id'],
                message_id=data['msg_id'],
                text="Обновление данных отменено",
                reply_markup=kb.back_to_menu_kb
            )
            await state.clear()
            return await self.wizard.exit()
        return await self.wizard.retake(step=previous_step)


    #Обработка кнопки перегенерировать
    @on.callback_query(F.data == "regenerate")
    async def regenerate_ya_answer(self, clbck: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        step = data['step']
        await self.wizard.retake(step=step + 1)


    #Обработка кнопки сохранить
    @on.callback_query(F.data == "save")
    async def save_ya_answer(self, clbck: CallbackQuery, bot: Bot , state: FSMContext) -> None:
        data = await state.get_data()
        print(data)
        await bot.edit_message_text(
            chat_id=data['chat_id'],
            message_id=data['msg_id'],
            text = "Сохранение данных в MemoryCode...",
        )

        api = await self.get_api(state, clbck.message.from_user.id)
        if api.access_token:
            updated_fields = {'epitaph': data['ya_answer']}
            updated_page = await api.update_memory_page(
                json.dumps(data['select_page']),
                json.dumps(updated_fields)
            )
            await bot.delete_message(chat_id=data['page_chat_id'], message_id=data['page_msg_id'])
            await bot.edit_message_text(
                    chat_id=data['chat_id'],
                    message_id=data['msg_id'],
                    text = "Данные сохранены",
                    reply_markup=kb.back_to_menu_kb
                )
        await state.clear()
        await self.wizard.exit()


    # Выбор существующего ответа
    @on.callback_query(F.data == "yes")
    async def stay_answer(self, clbck: CallbackQuery, state: FSMContext) -> None:
        data = await state.get_data()
        step = data['step']
        await self.wizard.retake(step=step + 1)  # Переход на on_enter()

    @on.callback_query(F.data == "no")
    async def edit_answer(self, clbck: CallbackQuery, state: FSMContext) -> None:
        await state.update_data(allow_msg=True)
        data = await state.get_data()
        step = data['step']
        msg = await clbck.message.answer(text="Напишите желаемый ответ")
        await state.update_data(
            change_field_chat_id = msg.chat.id,
            change_field_msg_id = msg.message_id
        )


    #Обработка кнопки отменить
    @on.callback_query(F.data == "cancel")
    async def cancel(self, clbck: CallbackQuery, bot: Bot, state: FSMContext) -> None:
        data = await state.get_data()
        await bot.delete_message(chat_id=data['page_chat_id'], message_id=data['page_msg_id'])
        await bot.edit_message_text(
            chat_id=data['chat_id'],
            message_id=data['msg_id'],
            text="Обновление данных отменено",
            reply_markup=kb.back_to_menu_kb
        )
        await state.clear()
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
    NameCallback.filter(F.tag == "page_choose" and F.edit_data == "epitaph")
)




#Сцена 2 - биографии
class BiographUpdateScene(Scene, state="about"):
    ...

about_router = Router(name=__name__)
about_router.callback_query.register(
    BiographUpdateScene.as_handler(),
    NameCallback.filter(F.tag == "page_choose" and F.edit_data == "biography")
)

