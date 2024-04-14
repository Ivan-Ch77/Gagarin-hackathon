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
import re

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
from bot.questions import (
    BIOGRAPH_QUESTIONS,
    EPITAPH_QUESTIONS
)
from bot.text import Text
from yandex.main import yandexGPT

text = Text()



"""Сцена 1 - для обработки эпитафий"""
class EpitaphUpdateScene(Scene, state="Epitaph"):

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
                        page_msg = await message.edit_text(f"Выбрана карточка {name} для описания эпитафии")
                    else:
                        page_msg = await message.edit_text(f"Выбрана карточка без названия для описания эпитафии")
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
            ya_answer = await yandexGPT(user_answers, epitaph=True)
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
            try:
                if page[key] and data['answers'][step]:
                    question.answer.text = data['answers'][step]
            except:
                if page[key]:
                    question.answer.text = page[key]
                else:
                    tmp_availiable = False

        # print(data)
        # В EPITAPH_QUESTIONS key не существует
        if tmp_availiable:
            text_ = question.text
            answers = data.get("answers", {})
            answers[step] = question.answer.text

            # Проверяем чтобы step == 0 and first_data is empty
            if not step and not first_data:
                message = await message.answer(
                    text = f"Вопрос {step+1}/{len(EPITAPH_QUESTIONS)}\n" + 'Для вопроса "' + text_ + f'" уже есть ответ:\n<b>{question.answer.text}</b>\nОставить его?',
                    reply_markup=kb.check_ready_answer_kb,
                )
            # Во всех случаях, когда step != 0 and first_data not empty
            else:
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
        await bot.edit_message_text(
            chat_id=data['chat_id'],
            message_id=data['msg_id'],
            text = "Сохранение данных в MemoryCode...",
        )

        api = await self.get_api(state, clbck.message.from_user.id)
        if api.access_token:
            updated_fields = {
                'name': data['answers'][0],
                'epitaph': data['ya_answer']
            }
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




"""Сцена 2 - биографии"""
class BiographUpdateScene(Scene, state="Biograph"):

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
    async def biography_on_enter(
        self,
        msg: CallbackQuery | Message,
        bot: Bot,
        state: FSMContext,
        step: int | None = 0
    ) -> Any:

        first_data = await state.get_data()
        if type(msg) == CallbackQuery:
            message = msg.message
        if not step and not first_data: # На самом первом шаге обрабатывается CallbackQuery на остальных Message
            clbck_data_id = NameCallback.unpack(msg.data).id
            api = await self.get_api(state, msg.from_user.id)
            if api.access_token:
                pages = await api.get_all_memory_pages()
                select_page = next((page for page in pages if str(clbck_data_id) == str(page['id'])), None)
                if select_page:
                    await state.update_data(select_page=select_page)
                    name = select_page['name']
                    if name:
                        page_msg = await message.edit_text(f"Выбрана карточка {name} для описания биографии")
                    else:
                        page_msg = await message.edit_text(f"Выбрана карточка без названия для описания биографии")
                    data = await state.update_data(
                        page_chat_id=page_msg.chat.id,
                        page_msg_id=page_msg.message_id
                    )

        try: # Остановка сцены когда заканчиваются вопросы
            question = BIOGRAPH_QUESTIONS[step]
        except IndexError:

            data = await state.get_data()
            await bot.edit_message_text(
                chat_id=data['chat_id'],
                message_id=data['msg_id'],
                text = "Создание биографии...",
            )
            select_page = data['select_page']
            answers = data['answers']
            user_answers = [value for value in answers.values()]
            ya_answer = await yandexGPT(user_answers, biography=True) # Функция для написания биографии
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

        # Пропуск вопросов на которые уже есть ответы
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

        elif type(key) == str:
            try:
                if page[key] and data['answers'][step]:
                    question.answer.text = data['answers'][step]
            except:
                if page[key]:
                    question.answer.text = page[key]
                else:
                    tmp_availiable = False

        # print(data)
        if tmp_availiable: # Есть данные для ответа на вопрос
            text_ = question.text
            answers = data.get("answers", {})
            answers[step] = question.answer.text

            if not step and not first_data:
                message = await message.answer(
                    text = f"Вопрос {step+1}/{len(BIOGRAPH_QUESTIONS)}\n" + 'Для вопроса "' + text_ + f'" уже есть ответ:\n<b>{question.answer.text}</b>\nОставить его?',
                    reply_markup=kb.check_ready_answer_kb,
                )
            else:
                message = await bot.edit_message_text(
                    chat_id=data['chat_id'],
                    message_id=data['msg_id'],
                    text = f"Вопрос {step+1}/{len(BIOGRAPH_QUESTIONS)}\n" + 'Для вопроса "' + text_ + f'" уже есть ответ:\n<b>{question.answer.text}</b>\nОставить его?',
                    reply_markup=kb.check_ready_answer_kb,
                )

            data = await state.update_data(
                answers=answers,
                allow_msg=False,
                chat_id=message.chat.id,
                msg_id=message.message_id
            )
        else: # Нет данных для ответа на вопрос
            text_ = question.text
            if not step and not first_data:
                message = await message.answer(
                    text = f"Вопрос {step+1}/{len(BIOGRAPH_QUESTIONS)}\n" + text_,
                    reply_markup=kb.necessary_q,
                )
            else:
                message = await bot.edit_message_text(
                    chat_id=data['chat_id'],
                    message_id=data['msg_id'],
                    text = f"Вопрос {step+1}/{len(BIOGRAPH_QUESTIONS)}\n" + text_,
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
        await bot.edit_message_text(
            chat_id=data['chat_id'],
            message_id=data['msg_id'],
            text = "Сохранение данных в MemoryCode...",
        )

        api = await self.get_api(state, clbck.message.from_user.id)
        if api.access_token:
            input_text = data['ya_answer']
            parts = re.split(r'\*\*(.*?)\*\*', input_text)
            parts = [part.strip() for part in parts if part.strip()]
            # Разбиение на заголовки и тексты
            biography_sections = []
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    title = parts[i]
                    description = parts[i + 1]
                    biography_sections.append({'title': title, 'description': description})

            selected_page = data['select_page']
            if 'filled_fields' not in selected_page:
                selected_page['filled_fields'] = []

            labels_to_add = {
                0: "biography_1",
                1: "biography_2",
                2: "end_of_biography"
            }
            for index in range(len(biography_sections)):
                label = labels_to_add.get(index)
                if label and label not in selected_page['filled_fields']:
                    selected_page['filled_fields'].append(label)

            if 'biographies' not in selected_page:
                selected_page['biographies'] = []
                selected_page['filled_fields'].append('biographies')

            # Теперь добавляем или обновляем существующие биографии
            current_biographies = selected_page['biographies']
            for index, section in enumerate(biography_sections):
                if index < len(current_biographies):
                    # Обновление существующих биографий
                    current_biographies[index]['title'] = section['title']
                    current_biographies[index]['description'] = section['description']
                else:
                    # Добавление новых биографий
                    new_biography = {
                        'id': None,
                        'title': section['title'],
                        'description': section['description'],
                        'page_id': selected_page['id'],
                        'created_at': None,
                        'updated_at': None,
                        'order': index + 1,
                        'checked': True
                    }
                    current_biographies.append(new_biography)

            updated_fields = {
                'name': data['answers'][0],
                'filled_fields': selected_page['filled_fields'],
                'biographies': current_biographies
            }
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
        await self.wizard.retake(step=step + 1)

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


    #Обработка выхода
    @on.callback_query.exit()
    @on.message.exit()
    async def exit(self, msg: Message | CallbackQuery, state: FSMContext) -> None:
        await state.set_data({})

about_router = Router(name=__name__)
about_router.callback_query.register(
    BiographUpdateScene.as_handler(),
    NameCallback.filter(F.tag == "page_choose" and F.edit_data == "biography")
)

