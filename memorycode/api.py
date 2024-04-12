import aiohttp
from memorycode.config import MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

async def get_access_token(email, password, device='bot-v0.0.1'):
    """
    Получает токен доступа для API MemoryCode.
    """
    url = f"{MEMORYCODE_BASE_URL}/api/v1/get-access-token"
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json={
            "email": email,
            "password": password,
            "device": device
        })
        data = await response.json()
        if 'access_token' in data:
            return data['access_token']
        else:
            return data  # Возвращает словарь с ошибкой

async def update_memory_page(initial_page_file, updated_fields_file, access_token):
    # Загрузка данных из файлов JSON
    with open(initial_page_file, 'r') as file:
        initial_page_data = json.load(file)
    with open(updated_fields_file, 'r') as file:
        updated_fields_data = json.load(file)

    # Обновление изначальных данных согласно второму файлу
    initial_page_data.update(updated_fields_data)

    url = f"{MEMORYCODE_BASE_URL}/page/{initial_page_data['id']}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {access_token}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.put(url, json=initial_page_data, headers=headers) as response:
            if response.status == 200:
                logger.info("Страница памяти успешно обновлена!")
            else:
                logger.error("Произошла ошибка при обновлении страницы памяти.")
                logger.error(f"Код ошибки: {response.status}")
                logger.error(f"Текст ошибки: {await response.text()}")


async def search_pages(access_token, query_params):
    url = f"{MEMORYCODE_BASE_URL}/page/search"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json", "Content-Type": "application/json;charset=UTF-8"}
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, headers=headers, json=query_params)
        return await response.json()

async def link_pages(access_token, link_data):
    url = f"{MEMORYCODE_BASE_URL}/page/relative"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, headers=headers, json=link_data)
        return await response.json()

async def get_individual_page_by_name(access_token, name):
    url = f"{MEMORYCODE_BASE_URL}/api/cabinet/individual-pages"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json", "Content-Type": "application/json;charset=UTF-8"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error("Ошибка при получении страницы памяти.")
                    logger.error(f"Код ошибки: {response.status}")
                    logger.error(f"Текст ошибки: {await response.text()}")
                    return None

                content_type = response.headers.get("Content-Type", "")
                if "application/json" not in content_type:
                    logger.error("Ошибка при получении страницы памяти: ожидался JSON, получен HTML.")
                    logger.error(f"Тип контента: {content_type}")
                    return None

                data = await response.json()
                # Ищем страницу по имени
                for page in data:
                    if isinstance(page, dict) and page.get('name') == name:
                        return page

                # Если страница не найдена
                logger.warning("Страница памяти не найдена.")
                return None
        except aiohttp.ClientError as e:
            logger.error("Ошибка при выполнении запроса:")
            logger.error(e)
            return None

async def get_all_memory_pages(access_token):
    url = f"{MEMORYCODE_BASE_URL}/api/cabinet/individual-pages"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json", "Content-Type": "application/json;charset=UTF-8"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error("Ошибка при получении всех страниц памяти.")
                    logger.error(f"Код ошибки: {response.status}")
                    logger.error(f"Текст ошибки: {await response.text()}")
                    return None

                content_type = response.headers.get("Content-Type", "")
                if "application/json" not in content_type:
                    logger.error("Ошибка при получении всех страниц памяти: ожидался JSON, получен HTML.")
                    logger.error(f"Тип контента: {content_type}")
                    return None

                data = await response.json()
                return data
        except aiohttp.ClientError as e:
            logger.error("Ошибка при выполнении запроса:")
            logger.error(e)
            return None


async def main():
    access_token = await get_access_token(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD)
    if access_token:
        pages_info = await get_all_memory_pages(access_token)
        print(pages_info)
        person_name = "Иванов Иван Иванович"
        page_info = await get_individual_page_by_name(access_token, person_name)
        logger.info(page_info)
        if page_info:
            logger.info("Информация о человеке:")
            logger.info("Имя:", page_info.get('name'))
            logger.info("Дата рождения:", page_info.get('birthday_at'))
            logger.info("Дата смерти:", page_info.get('died_at'))
            logger.info("Эпитафия:", page_info.get('epitaph'))
        else:
            logger.info(f"Страница с именем '{person_name}' не найдена.")
    else:
        logger.error("Не удалось получить токен доступа.")

asyncio.run(main())