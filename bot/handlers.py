from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from .states import DataCollectionForm
from yandex.api import fetch_from_yandexgpt
from yandex.config import CATALOG_ID

async def send_welcome(message: types.Message):
    """
    Отправляет приветственное сообщение и предлагает начать сбор данных.
    :param message: объект сообщения от пользователя
    """
    await message.reply("Привет! Я бот, который поможет тебе собрать и сохранить информацию об умершем человеке. Напиши /start, чтобы начать.")

async def start_form(message: types.Message):
    """
    Начинает процесс сбора данных, устанавливая первое состояние FSM.
    :param message: объект сообщения от пользователя
    """
    await DataCollectionForm.full_name.set()
    await message.reply("Введите, пожалуйста, полное ФИО умершего.")

async def process_full_name(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод ФИО умершего и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['full_name'] = message.text.strip()
    await DataCollectionForm.date_of_birth.set()
    await message.reply("Укажите дату рождения умершего (формат ГГГГ-ММ-ДД).")

async def process_date_of_birth(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод даты рождения и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['date_of_birth'] = message.text
    await DataCollectionForm.date_of_death.set()
    await message.reply("Теперь введите дату смерти (формат ГГГГ-ММ-ДД).")

async def process_date_of_death(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод даты смерти и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['date_of_death'] = message.text
    await DataCollectionForm.place_of_birth.set()
    await message.reply("Какое место рождения у умершего?")

async def process_place_of_birth(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод места рождения и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['place_of_birth'] = message.text
    await DataCollectionForm.place_of_death.set()
    await message.reply("Укажите место смерти умершего.")

async def process_place_of_death(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод места смерти и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['place_of_death'] = message.text
    await DataCollectionForm.citizenship.set()
    await message.reply("Какое было гражданство у умершего?")

async def process_citizenship(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод гражданства умершего и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['citizenship'] = message.text
    await DataCollectionForm.children.set()
    await message.reply("Есть ли у умершего дети? (ответьте 'да' или 'нет')")

async def process_children(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод информации о детях умершего и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['children'] = message.text.lower() == 'да'
    await DataCollectionForm.spouse.set()
    await message.reply("Если был супруг или супруга, укажите их ФИО (или напишите 'нет').")

async def process_spouse(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод информации о супруге умершего и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['spouse'] = message.text
    await DataCollectionForm.education.set()
    await message.reply("Укажите, какое образование имел умерший.")

async def process_education(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод информации об образовании умершего и переходит к следующему шагу.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['education'] = message.text
    await DataCollectionForm.career.set()
    await message.reply("Чем занимался умерший? Укажите его профессию или род деятельности.")

async def process_career(message: types.Message, state: FSMContext):
    """
    Обрабатывает ввод информации о карьере умершего и переходит к последнему шагу для создания эпитафии.
    :param message: объект сообщения от пользователя
    :param state: контекст состояния FSM
    """
    async with state.proxy() as data:
        data['career'] = message.text
    await DataCollectionForm.epitaph.set()
    await message.reply("Введите ключевую информацию для создания эпитафии.")


async def process_epitaph(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    prompt_messages = [
        {"role": "system", "text": "Задача: создать эпитафию."},
        {"role": "user", "text": "Мне нужна эпитафия, основанная на данных, которые я предоставил."},
        {"role": "assistant", "text": "Пожалуйста, предоставьте подробную информацию о человеке для создания эпитафии."},
        {"role": "user", "text": f"Имя: {user_data['full_name']}, родился: {user_data['date_of_birth']}, умер: {user_data['date_of_death']}, место рождения: {user_data['place_of_birth']}, место смерти: {user_data['place_of_death']}, род деятельности: {user_data['career']}, гражданство: {user_data['citizenship']}."}
    ]
    epitaph_response = await fetch_from_yandexgpt(prompt_messages, CATALOG_ID)
    if epitaph_response and 'completions' in epitaph_response:
        epitaph = epitaph_response['completions'][0]['text']
        await state.update_data(epitaph=epitaph)
        await DataCollectionForm.biography.set()
        await message.reply(f"Эпитафия для {user_data['full_name']}:\n{epitaph}\nПожалуйста, расскажите более подробно о его жизни для создания биографии.")
    else:
        await message.reply("Произошла ошибка при создании эпитафии. Пожалуйста, попробуйте снова.")

async def process_biography(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    prompt_messages = [
        {"role": "system", "text": "Задача: создать биографию."},
        {"role": "user", "text": "Я хочу создать детализированную биографию умершего, используя собранную информацию."},
        {"role": "assistant", "text": "Хорошо, дайте мне всю доступную информацию для составления биографии."},
        {"role": "user", "text": f"Имя умершего: {user_data['full_name']}, дата рождения: {user_data['date_of_birth']}, дата смерти: {user_data['date_of_death']}, профессия: {user_data['career']}, место жительства: {user_data['place_of_birth']}, сведения о супруге: {user_data['spouse']}, образование: {user_data['education']}."}
    ]
    biography_response = await fetch_from_yandexgpt(prompt_messages, CATALOG_ID)
    if biography_response and 'completions' in biography_response:
        biography = biography_response['completions'][0]['text']
        await state.finish()
        await message.reply(f"Биография умершего:\n{biography}\nСпасибо за использование нашего сервиса.")
    else:
        await message.reply("Произошла ошибка при создании биографии. Пожалуйста, попробуйте снова.")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'])
    dp.register_message_handler(start_form, commands=['start'])
    dp.register_message_handler(process_full_name, state=DataCollectionForm.full_name)
    dp.register_message_handler(process_date_of_birth, state=DataCollectionForm.date_of_birth)
    dp.register_message_handler(process_date_of_death, state=DataCollectionForm.date_of_death)
    dp.register_message_handler(process_place_of_birth, state=DataCollectionForm.place_of_birth)
    dp.register_message_handler(process_place_of_death, state=DataCollectionForm.place_of_death)
    dp.register_message_handler(process_citizenship, state=DataCollectionForm.citizenship)
    dp.register_message_handler(process_children, state=DataCollectionForm.children)
    dp.register_message_handler(process_spouse, state=DataCollectionForm.spouse)
    dp.register_message_handler(process_education, state=DataCollectionForm.education)
    dp.register_message_handler(process_career, state=DataCollectionForm.career)
    dp.register_message_handler(process_epitaph, state=DataCollectionForm.epitaph)
    dp.register_message_handler(process_biography, state=DataCollectionForm.biography)
