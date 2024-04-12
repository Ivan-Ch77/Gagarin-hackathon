import aiohttp
from memorycode.config import MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL
import asyncio
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def get_access_token(email: str, password: str, device: str = 'bot-v0.0.1') -> str | dict:
    """
    Асинхронно получает токен доступа к API MemoryCode.

    Args:
        email (str): Email пользователя для аутентификации.
        password (str): Пароль пользователя.
        device (str): Описание устройства или клиента, делающего запрос (по умолчанию 'bot-v0.0.1').

    Returns:
        Union[str, dict]: Возвращает строку с токеном доступа или словарь с ошибкой, если аутентификация не удалась.
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


async def update_memory_page(initial_page_file: str, updated_fields_file: str, access_token: str) -> None:
    # TODO:На данный момент возвращает ошибку: Произошла ошибка при обновлении страницы памяти.
    # TODO:Код ошибки: 404
    # TODO:Текст ошибки: {"message": "No query results for model [App\\Models\\Page\\Page]."}
    """
    Асинхронно обновляет данные страницы памяти в системе MemoryCode.

    Args:
        initial_page_file (str): JSON-строка с исходными данными страницы.
        updated_fields_file (str): JSON-строка с полями для обновления.
        access_token (str): Токен доступа к API.

    """
    # # Загрузка данных из файлов JSON
    # with open(initial_page_file, 'r') as file:
    #     initial_page_data = json.load(file)
    # with open(updated_fields_file, 'r') as file:
    #     updated_fields_data = json.load(file)
    # Загрузка данных из JSON строк
    initial_page_data = json.loads(initial_page_file)
    updated_fields_data = json.loads(updated_fields_file)

    # Обновление изначальных данных согласно второму файлу
    initial_page_data.update(updated_fields_data)
    url = f"{MEMORYCODE_BASE_URL}/api/page/{initial_page_data['id']}"
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


async def search_pages(access_token: str, query_params: dict) -> dict:
    # TODO: Нуждается в реализации полной
    """
    Асинхронно выполняет поиск страниц памяти по заданным критериям.

    Args:
        access_token (str): Токен доступа к API.
        query_params (dict): Параметры поиска.

    Returns:
        dict: Результаты поиска в формате JSON.
    """
    url = f"{MEMORYCODE_BASE_URL}/page/search"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json",
               "Content-Type": "application/json;charset=UTF-8"}
    async with aiohttp.ClientSession() as session:
        response = await session.post(url, headers=headers, json=query_params)
        return await response.json()


async def link_pages(access_token: str, link_data: dict) -> dict:
    # TODO: Нуждается в реализации полной
    """
    Асинхронно связывает страницы памяти друг с другом в системе MemoryCode.

    Args:
        access_token (str): Токен доступа к API.
        link_data (dict): Данные для связывания страниц.

    Returns:
        dict: Результат операции в формате JSON.
    """


async def get_individual_page_by_name(access_token: str, name: str) -> Optional[str]:
    """
    Асинхронно извлекает страницу памяти по имени.

    Args:
        access_token (str): Токен доступа к API.
        name (str): Имя для поиска страницы.

    Returns:
        Optional[str]: JSON-строка с данными страницы или None, если страница не найдена.
    """
    url = f"{MEMORYCODE_BASE_URL}/api/cabinet/individual-pages"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json",
               "Content-Type": "application/json;charset=UTF-8"}

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
                        return json.dumps(page)

                # Если страница не найдена
                logger.warning("Страница памяти не найдена.")
                return None
        except aiohttp.ClientError as e:
            logger.error("Ошибка при выполнении запроса:")
            logger.error(e)
            return None


async def get_all_memory_pages(access_token: str) -> Optional[dict]:
    """
    Асинхронно извлекает все страницы памяти из системы MemoryCode.

    Args:
        access_token (str): Токен доступа к API.

    Returns:
        Optional[dict]: Список всех страниц в формате JSON или None в случае ошибки.
    """
    url = f"{MEMORYCODE_BASE_URL}/api/cabinet/individual-pages"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json",
               "Content-Type": "application/json;charset=UTF-8"}

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
        logger.info("Все карточки:", pages_info)
        person_name = "Иванов Иван Иванович"
        page_info = await get_individual_page_by_name(access_token, person_name)
        initial_page_file = page_info
        updated_fields_file = {'epitaph': "Чел хорош"}
        updated_fields_file = json.dumps(updated_fields_file)
        updated_page = await update_memory_page(initial_page_file, updated_fields_file, access_token)
        page_info = json.loads(page_info)
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
