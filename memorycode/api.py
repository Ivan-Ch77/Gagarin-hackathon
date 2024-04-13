import aiohttp
from memorycode.config import MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL
from memorycode.wraps import require_auth
import asyncio
import json
import logging
from typing import Optional
from aiohttp import FormData

# Настройка базового логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Создание логгера
logger = logging.getLogger(__name__)



class MemoryCodeAPI:
    def __init__(self, email: str, password: str, base_url: str):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.access_token = None
        self.memory_pages = None

    async def authenticate(self) -> str | dict:
        url = f"{self.base_url}/api/v1/get-access-token"
        async with aiohttp.ClientSession() as session:
            response = await session.post(url, json={
                "email": self.email,
                "password": self.password,
                "device": 'bot-v0.0.1'
            })
            data = await response.json()
            if 'access_token' in data:
                self.access_token = data['access_token']
                return self.access_token
            else:
                logger.error("Ошибка аутентификации: {}".format(data))
                return data  # Возвращает словарь с ошибкой

    @require_auth
    async def get_all_memory_pages(self) -> str | dict:
        """
        Асинхронно извлекает все страницы памяти из системы MemoryCode.

        Args:
            access_token (str): Токен доступа к API.

        Returns:
            Optional[dict]: Список всех страниц в формате JSON или None в случае ошибки.
        """

        url = f"{MEMORYCODE_BASE_URL}/api/cabinet/individual-pages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        logger.error("Ошибка при получении всех страниц памяти.")
                        logger.error(f"Код ошибки: {response.status}")
                        logger.error(f"Текст ошибки: {await response.text()}")
                        return "Ошибка при получении всех страниц памяти."

                    content_type = response.headers.get("Content-Type", "")
                    if "application/json" not in content_type:
                        logger.error("Ошибка при получении всех страниц памяти: ожидался JSON, получен HTML.")
                        logger.error(f"Тип контента: {content_type}")
                        return "Ошибка при получении всех страниц памяти: ожидался JSON, получен HTML."

                    self.memory_pages = await response.json()
                    return self.memory_pages
            except aiohttp.ClientError as e:
                logger.error("Ошибка при выполнении запроса:")
                logger.error(e)
                return f"Ошибка при выполнении запроса: {e}"

    @require_auth
    async def get_individual_page_by_name(self, name: str) -> str:
        """
        Асинхронно извлекает страницу памяти по имени.

        Args:
            access_token (str): Токен доступа к API.
            name (str): Имя для поиска страницы.

        Returns:
            Optional[str]: JSON-строка с данными страницы или None, если страница не найдена.
        """

        for page in self.memory_pages:
            if isinstance(page, dict) and page.get('name') == name:
                logger.info(f"Страница по имени {name} найдена!")
                return json.dumps(page)

        logger.warning("Страница памяти не найдена.")
        return "Страница памяти не найдена."

    @require_auth
    async def update_memory_page(self, initial_page_file: str, updated_fields_file: str) -> str:
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

        page_exists = any(page.get('slug') == initial_page_data['slug'] for page in self.memory_pages if isinstance(page, dict))
        if not page_exists:
            logger.error(f"Страница с slug {initial_page_data['slug']} не найдена.")
            return f"Страница с slug {initial_page_data['slug']} не найдена."

        logger.info(f"Страница с slug {initial_page_data['slug']} найдена.")
        initial_page_data.update(updated_fields_data)

        url = f"{MEMORYCODE_BASE_URL}/api/page/{initial_page_data['slug']}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8"
        }

        async with aiohttp.ClientSession() as session:
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
                return f"Ошибка при обновлении страницы памяти, код ошибки: {response.status}"

    @require_auth
    async def link_page(self, page_to_link: dict, current_page: dict) -> bool:
        """
        Асинхронно связывает страницу с другой страницей в системе MemoryCode.

        Args:
            access_token (str): Токен доступа к API.
            page_to_link (dict): Словарь с данными страницы, которую хотим привязать.
            current_page (dict): Словарь с данными текущей страницы.

        Returns:
            bool, информация об успехе операции
        """

        url = f"{MEMORYCODE_BASE_URL}/api/page/search"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
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
                return False

    @require_auth
    async def send_link_request(self, current_page: dict, linked_page: dict, kinship: int) -> bool:
        """
        Отправляет запрос на связывание страниц памяти владельцу указанной страницы.

        Args:
            current_page (dict): Словарь с данными текущей страницы.
            linked_page (dict): Словарь с данными страницы для связывания.
            kinship (int): Родственная связь между страницами.
            access_token (str): Токен доступа к API.

        Returns:
            bool: True если связывание прошло успешно, иначе False.
        """

        valid_kinships = set(range(1, 15))
        if kinship not in valid_kinships:
            logger.error(f"Недопустимое значение родственной связи: {kinship}")
            raise ValueError(f"Родственная связь должна быть одним из следующих значений: {valid_kinships}")

        url = f"{MEMORYCODE_BASE_URL}/api/page/relative"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8"
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
                        return False
                else:
                    error_message = await response.text()
                    response_data = json.loads(error_message)
                    logger.error(
                        f"Ошибка при отправке предложения на связывания страниц, код ошибки: {response.status}")
                    logger.error(f"Основное сообщение об ошибке: {response_data.get('message', '')}")
                    if 'errors' in response_data:
                        logger.error("Детали ошибок:")
                        for field, messages in response_data['errors'].items():
                            for message in messages:
                                logger.error(f" - {field}: {message}")
                    return False

    @require_auth
    async def upload_photo(self, file_path: str) -> dict:
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
            "Authorization": f"Bearer {self.access_token}",
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

    @require_auth
    async def add_comment_to_page(self, page_id: int, comment_data: dict) -> dict:
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
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json;charset=UTF-8"
        }

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
    # Создание экземпляра класса
    api = MemoryCodeAPI(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD, MEMORYCODE_BASE_URL)
    # Аутентификация и получение токена доступа
    access_token = await api.authenticate()
    if access_token:
        # Получение информации о всех страницах
        pages_info = await api.get_all_memory_pages()

        # Получение информации о конкретных страницах
        person_name = "Команда Хакатон 10/1"
        page_info_1 = await api.get_individual_page_by_name(person_name)
        person_name = "Команда Хакатон 10/2"
        page_info_2 = await api.get_individual_page_by_name(person_name)

        if page_info_1 and page_info_2:
            # Загрузка фотографии
            photo = await api.upload_photo('../../../Downloads/lotus-3192656_640.png')

            # Обновление страницы с новыми данными
            updated_fields = {'epitaph': "Чел хорош вдвойне"}
            updated_page = await api.update_memory_page(page_info_1, json.dumps(updated_fields))

            # Связывание двух страниц
            if page_info_1 and page_info_2:
                linked = await api.link_page(json.loads(page_info_1), json.loads(page_info_2))
                logger.info(f"Linked: {linked}")

            # Отправка запроса на связывание страниц
            send = await api.send_link_request(json.loads(page_info_1), json.loads(page_info_2), kinship=5)
            logger.info(f"Send link request: {send}")

            # Добавление комментария к странице
            comment_data = {
                "photo": {"url": photo.get('url', '')},
                "fio": "ИМЯ / ФАМИЛИЯ",
                "email": "",
                "text": "СЛОВА",
                "relation_role": "Бабушка",
                "checked": True,
                "hasEmail": False
            }
            comment = await api.add_comment_to_page(8757, comment_data)
            logger.info(f"comment: {comment}")
        else:
            logger.error("Ошибка: Не удалось получить информацию о страницах.")
    else:
        logger.error("Не удалось получить токен доступа.")

# Запуск основной корутины
if __name__ == "__main__":
    asyncio.run(main())