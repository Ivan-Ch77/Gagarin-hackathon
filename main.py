import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiohttp import ClientSession
from dotenv import load_dotenv
import os


load_dotenv()
API_KEY_TG = os.getenv('API_KEY_TG')
API_KEY_YA = os.getenv('API_KEY_YA')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bot = Bot(token=API_KEY_TG)
dp = Dispatcher(bot)


session = ClientSession()

class DataCollectionForm(StatesGroup):
    full_name = State()  # ФИО
    date_of_birth = State()  # дата рождения
    date_of_death = State()  # дата смерти
    place_of_birth = State()  # место рождения
    place_of_death = State()  # место смерти
    citizenship = State()  # гражданство
    children = State()  # дети
    spouse = State()  # супруг(а)
    education = State()  # образование
    career = State()  # род деятельности
    epitaph = State()  # эпитафия (генерация GPT)
    biography = State()  # биография (генерация GPT)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот, который поможет тебе заполнить сложные формы. Напиши мне что-нибудь!")


async def fetch_from_yandexgpt(prompt):
    url = 'https://api.aicloud.yandex.net/v1/yandex/gpt3/predict'
    headers = {
        'Authorization': f'Bearer {API_KEY_YA}',
        'Content-Type': 'application/json',
    }
    payload = {
        'prompt': prompt,
        'length': 50,
    }
    async with session.post(url, headers=headers, json=payload) as response:
        if response.status == 200:
            return await response.json()
        else:
            error_message = await response.text()
            logger.error(f'Ошибка API YandexGPT: {response.status}, тело ответа: {error_message}')
            return None


@dp.message_handler(commands=['start'])
async def start_form(message: types.Message):
    await DataCollectionForm.full_name.set()
    await message.reply("Пожалуйста, введите ФИО умершего полностью.")

@dp.message_handler(state=DataCollectionForm.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    """
    Обработчик для получения ФИО умершего.
    """
    full_name = message.text.strip()
    #TODO: Валидация имени?
    async with state.proxy() as data:
        data['full_name'] = full_name
    await DataCollectionForm.next()
    await message.reply("Какова дата рождения умершего? (формат ГГГГ-ММ-ДД)")


@dp.message_handler(state=DataCollectionForm.date_of_birth)
async def process_date_of_birth(message: types.Message, state: FSMContext):
    #TODO: Реализовать проверку введённой даты на корректность
    async with state.proxy() as data:
        data['date_of_birth'] = message.text
    await DataCollectionForm.next()
    await message.reply("Укажите дату смерти (формат ГГГГ-ММ-ДД).")

@dp.message_handler(state=DataCollectionForm.date_of_death)
async def process_date_of_death(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date_of_death'] = message.text
    await DataCollectionForm.next()
    await message.reply("Укажите место рождения.")

@dp.message_handler(state=DataCollectionForm.place_of_birth)
async def process_place_of_birth(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['place_of_birth'] = message.text
    await DataCollectionForm.next()
    await message.reply("Укажите место смерти.")

# Обработчик для поля "спутник жизни"
@dp.message_handler(state=DataCollectionForm.spouse)
async def process_spouse(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['spouse'] = message.text
    await DataCollectionForm.next()
    await message.reply("Какое у вас образование?")

# Обработчик для поля "образование"
@dp.message_handler(state=DataCollectionForm.education)
async def process_education(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['education'] = message.text
    await DataCollectionForm.next()
    await message.reply("Чем вы занимались? Какова ваша профессия или род деятельности?")

# Обработчик для поля "род деятельности"
@dp.message_handler(state=DataCollectionForm.career)
async def process_career(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['career'] = message.text
    await DataCollectionForm.epitaph.set()
    await message.reply("Пожалуйста, введите основные данные для создания эпитафии.")

# Обработчик для поля "эпитафия"
@dp.message_handler(state=DataCollectionForm.epitaph)
async def process_epitaph(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    prompt = f"Создайте эпитафию для человека с именем {user_data['full_name']}, датой рождения {user_data['date_of_birth']}, и датой смерти {user_data['date_of_death']}."
    epitaph_response = await fetch_from_yandexgpt(prompt)
    if epitaph_response and 'text' in epitaph_response:
        epitaph = epitaph_response['text']
        await state.update_data(epitaph=epitaph)
        await DataCollectionForm.next()
        await message.reply(f"Эпитафия: {epitaph}\nТеперь, пожалуйста, расскажите немного о себе для создания биографии.")
    else:
        await message.reply("Произошла ошибка при создании эпитафии. Пожалуйста, попробуйте ещё раз.")

# Обработчик для поля "биография"
@dp.message_handler(state=DataCollectionForm.biography)
async def process_biography(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    prompt = f"Напишите биографию для человека с именем {user_data['full_name']} и жизненной историей: {user_data['career']}."
    biography_response = await fetch_from_yandexgpt(prompt)
    if biography_response and 'text' in biography_response:
        biography = biography_response['text']
        await state.finish()
        await message.reply(f"Биография:\n{biography}\n\nСпасибо за использование нашего бота.")
    else:
        await message.reply("Произошла ошибка при создании биографии. Пожалуйста, попробуйте ещё раз.")

async def on_startup(dispatcher):
    logger.info("Бот запущен!")

async def on_shutdown(dispatcher):
    logger.info("Бот останавливается...")
    await session.close()

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)