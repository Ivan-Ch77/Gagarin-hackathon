import aiohttp
from memorycode.config import MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL
import asyncio
import json
import logging
from typing import Optional
from aiohttp import FormData

# Настройка базового логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Создание логгера
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



async def update_memory_page(initial_page_file: str, updated_fields_file: str, access_token: str) -> str:
    """
    Асинхронно обновляет данные страницы памяти в системе MemoryCode.

    Args:
        initial_page_file (str): JSON-строка с исходными данными страницы.
        updated_fields_file (str): JSON-строка с полями для обновления.
        access_token (str): Токен доступа к API.

    Returns:
        str: Ответ сервера в формате JSON или сообщение об ошибке.
    """
    initial_page_data = json.loads(initial_page_file)
    updated_fields_data = json.loads(updated_fields_file)

    url = f"{MEMORYCODE_BASE_URL}/api/cabinet/individual-pages"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {access_token}"
    }

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, headers=headers)
        if response.status != 200:
            error_message = await response.text()
            logger.error(f"Ошибка при получении списка страниц: {error_message}")
            return None

        data = await response.json()
        page_exists = any(page.get('slug') == initial_page_data['slug'] for page in data if isinstance(page, dict))
        if not page_exists:
            logger.error(f"Страница с slug {initial_page_data['slug']} не найдена.")
            return None

        logger.info(f"Страница с slug {initial_page_data['slug']} найдена.")
        initial_page_data.update(updated_fields_data)
        url = f"{MEMORYCODE_BASE_URL}/api/page/{initial_page_data['slug']}"

        response = await session.put(url, json=initial_page_data, headers=headers)
        if response.status == 200:
            logger.info("Страница памяти успешно обновлена!")
            data = await response.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        else:
            error_message = await response.text()
            response_data = json.loads(error_message)
            logger.error(f"Ошибка при обновлении страницы памяти, код ошибки: {response.status}")
            logger.error(f"Основное сообщение об ошибке: {response_data.get('message', '')}")
            if 'errors' in response_data:
                logger.error("Детали ошибок:")
                for field, messages in response_data['errors'].items():
                    for message in messages:
                        logger.error(f" - {field}: {message}")
            return None


async def link_page(access_token: str, page_to_link: dict, current_page: dict) -> Optional[bool]:
    """
    Асинхронно связывает страницу с другой страницей в системе MemoryCode.

    Args:
        access_token (str): Токен доступа к API.
        page_to_link (dict): Словарь с данными страницы, которую хотим привязать.
        current_page (dict): Словарь с данными текущей страницы.

    Returns:
        None: Выводит результат выполнения операции в лог.
    """
    url = f"{MEMORYCODE_BASE_URL}/api/page/search"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8"
    }
    body = {
        "name": page_to_link.get("name", ""),
        "slug": page_to_link["slug"],
        "birthday_at": page_to_link.get("birthday_at", ""),
        "died_at": page_to_link.get("died_at", ""),
        "slugs": [current_page["slug"]],
        "published_page": 1,
        "page": {"isTrusted": True}
    }

    async with aiohttp.ClientSession() as session:
        response = await session.post(url, json=body, headers=headers)
        if response.status == 200:
            logger.info(f"Страницы успешно связаны: {current_page['slug']} -> {page_to_link['slug']}")
            return True
        else:
            error_message = await response.text()
            logger.error(f"Ошибка при связывании страниц: {error_message}")



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


async def send_link_request(access_token: str, current_page: dict, linked_page: dict, kinship: int) -> Optional[bool]:
    """
    Отправляет запрос на связывание страниц памяти владельцу указанной страницы.

    Args:
        current_page (dict): Словарь с данными текущей страницы.
        linked_page (dict): Словарь с данными страницы для связывания.
        kinship (int): Родственная связь между страницами.
        access_token (str): Токен доступа к API.

    Returns:
        Optional[bool]: True если связывание прошло успешно, иначе None.
    """
    valid_kinships = set(range(1, 15))
    if kinship not in valid_kinships:
        logger.error(f"Недопустимое значение родственной связи: {kinship}")
        raise ValueError(f"Родственная связь должна быть одним из следующих значений: {valid_kinships}")

    url = f"{MEMORYCODE_BASE_URL}/api/page/relative"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "parentId": current_page.get("id"),  # ID текущей страницы
        "relation": linked_page.get("slug"),  # Slug связываемой страницы
        "kinship": kinship  # Родственная связь
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success', False):
                    logger.info("Успешно отправлено предложения на связывание страниц.")
                    return True
                else:
                    logger.error("Не удалось отправить предложение на связывание страниц.")
                    return None
            else:
                error_message = await response.text()
                response_data = json.loads(error_message)
                logger.error(f"Ошибка при отправке предложения на связывания страниц, код ошибки: {response.status}")
                logger.error(f"Основное сообщение об ошибке: {response_data.get('message', '')}")
                if 'errors' in response_data:
                    logger.error("Детали ошибок:")
                    for field, messages in response_data['errors'].items():
                        for message in messages:
                            logger.error(f" - {field}: {message}")
                return None

async def upload_photo(access_token: str, file_path: str) -> dict:
    """
    Асинхронно загружает фотографию на сервер.

    Args:
        file_path (str): Путь к файлу фотографии, который нужно загрузить.
        access_token (str): Токен доступа к API.

    Returns:
        dict: Словарь с информацией о загруженной фотографии.

    Raises:
        Exception: Если произошла ошибка при загрузке.
    """
    url = f"{MEMORYCODE_BASE_URL}/api/media/upload"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ru,en;q=0.9",
        "Connection": "keep-alive",
        "Authorization": f"Bearer {access_token}"
    }

    data = FormData()
    data.add_field('file',
                   open(file_path, 'rb'),
                   filename=file_path.split('/')[-1],
                   content_type='multipart/form-data')

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                logger.info("Фотография успешно загружена.")
                return result
            else:
                error_message = await response.text()
                logger.error(f"Ошибка при загрузке фотографии: {error_message}")
                raise Exception(f"Ошибка при загрузке: {error_message}")


async def add_comment_to_page(access_token: str, page_id: int, comment_data: dict) -> dict:
    """
    Отправляет POST-запрос на добавление комментария к странице памяти.

    Args:
        page_id (int): ID страницы памяти.
        comment_data (dict): Словарь с данными комментария.
        access_token (str): Токен доступа к API.

    Returns:
        dict: Ответ от сервера в формате JSON.

    Raises:
        Exception: Если произошла ошибка при отправке запроса.
    """
    url = f"{MEMORYCODE_BASE_URL}/api/comment"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {access_token}"
    }

    # Формируем тело запроса
    payload = {
        "page_id": page_id,
        "photo": comment_data["photo"],
        "fio": comment_data["fio"],
        "email": comment_data.get("email", ""),
        "text": comment_data["text"],
        "relation_role": comment_data["relation_role"],
        "checked": comment_data["checked"],
        "hasEmail": comment_data.get("hasEmail", False)
    }

    async with aiohttp.ClientSession() as session:
        try:
            response = await session.post(url, headers=headers, json=payload)
            response_data = await response.json()
            if response.status == 200:
                logger.info("Комментарий успешно добавлен.")
                return response_data
            else:
                logger.error(f"Ошибка при добавлении комментария: {response.status} {response_data}")
                return response_data
        except Exception as e:
            logger.error(f"Произошла ошибка при отправке запроса: {str(e)}")
            return {"error": "Failed to send request", "details": str(e)}



async def main():
    access_token = await get_access_token(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD)
    if access_token:
        pages_info = await get_all_memory_pages(access_token)
        print(pages_info)
        person_name = "Команда Хакатон 10/1"
        page_info_1 = await get_individual_page_by_name(access_token, person_name)
        person_name = "Команда Хакатон 10/2"
        page_info_2 = await get_individual_page_by_name(access_token, person_name)
        initial_page_file = page_info_1
        photo = await upload_photo(access_token, file_path='../../../Downloads/lotus-3192656_640.png')
        updated_fields_file = {'epitaph': "Чел хорош вдвойне",}
        updated_fields_file = json.dumps(updated_fields_file)
        updated_page = await update_memory_page(initial_page_file, updated_fields_file, access_token)
        await link_page(access_token, json.loads(page_info_1), json.loads(page_info_2))
        send = await send_link_request(access_token, json.loads(page_info_1), json.loads(page_info_2), kinship=5)

        comment_data = {
            "photo": {
                "url": ""
            },
            "fio": "ИМЯ / ФАМИЛИЯ",
            "email": "",
            "text": "СЛОВА",
            "relation_role": "Бабушка",
            "checked": True,
            "hasEmail": False
        }
        comment = await add_comment_to_page(access_token, page_id=8757, comment_data=comment_data)
        print(comment)

    else:
        logger.error("Не удалось получить токен доступа.")

asyncio.run(main())
