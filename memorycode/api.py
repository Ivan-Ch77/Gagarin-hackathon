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

async def update_memory_page(page_id, access_token):
    url = f"{MEMORYCODE_BASE_URL}/page/{page_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "id": 148,
        "name": "haha Виталий haha",
        "surname": None,
        "patronym": None,
        "birthday_at": "1700-01-02 00:00:00",
        "died_at": "1700-01-03 00:00:00",
        "epitaph": "КРАТКАЯ ЭПИТАФИЯ",
        "author_epitaph": "АВТОР ЭПИТАФИИ",
        "video_links": [
            {
                "url": "https://www.youtube.com/watch?v=figIDuctqMY",
                "enabled": True
            }
        ],
        "external_links": [
            {
                "link": "https://www.youtube.com/watch?v=figIDuctqMY",
                "link_name": "Блондинка за углом - YouTube",
                "enabled": True
            }
        ],
        "published_page": True,
        "accessible_by_password": False,
        "access_password": None,
        "user_id": 6,
        "master_id": None,
        "page_type_id": 1,
        "created_at": "2023-12-28T06:36:02.000000Z",
        "updated_at": "2023-12-28T07:17:13.000000Z",
        "deleted_at": None,
        "slug": 23647620,
        "burial_id": None,
        "price": None,
        "commission": None,
        "video_images": [
            {
                "image": "https://i.ytimg.com/vi/figIDuctqMY/hqdefault.jpg",
                "src": "https://www.youtube.com/embed/figIDuctqMY?feature=oembed?autoplay=1"
            }
        ],
        "payment_id": None,
        "blank_id": None,
        "is_blank": False,
        "is_vip": False,
        "views": 0,
        "visitors": 0,
        "lead_id": None,
        "index_page": True,
        "filled_fields": [
            "biography_1",
            "biography_2",
            "biography_3",
            "end_of_biography",
            "epitaph"
        ],
        "position": None,
        "is_referral": False,
        "banner_enabled": True,
        "locale": None,
        "was_indexed": False,
        "qr_hidden": False,
        "historical_status_id": 1,
        "count_filled_fields": 5,
        "parent_tree_id": 14,
        "custom_birthday_at": "12",
        "custom_died_at": "13",
        "pages": [],
        "photos": [
            {
                "id": 66,
                "url": "https://src.mc.dev.rand.agency/storage/test/66/1712092161.jpg",
                "name": "media-librarys0UDAC",
                "custom_properties": {
                    "name": "5. ФОТОГАЛЕРЕЯ",
                    "desc": "5. ФОТОГАЛЕРЕЯ",
                    "position": 0
                }
            }
        ],
        "audio_records": [],
        "video_records": [],
        "video_previews": [],
        "itemComments": [
            {
                "title": "Опубликованные отзывы",
                "comments": [
                    {
                        "id": 1,
                        "fio": "ИМЯ / ФАМИЛИЯ",
                        "text": "СЛОВА",
                        "relation_role": "КЕМ ПРИХОДИТСЯ?",
                        "page_id": 148,
                        "created_at": "2024-04-02T21:13:36.000000Z",
                        "updated_at": "2024-04-02T21:13:36.000000Z",
                        "email": None,
                        "checked": True,
                        "is_allowed": True,
                        "deleted_at": None,
                        "photo": {
                            "id": 68,
                            "url": "https://src.mc.dev.rand.agency/storage/app/public/68/1712092416.jpg"
                        },
                        "media": [
                            {
                                "id": 68,
                                "model_type": "App\\Models\\Comment\\Comment",
                                "model_id": 1,
                                "uuid": "f149f59f-53fe-4290-8ee0-15ee93dc7bea",
                                "collection_name": "photos",
                                "name": "media-libraryC40593",
                                "file_name": "1712092416.jpg",
                                "mime_type": "image/jpeg",
                                "disk": "public",
                                "conversions_disk": "public",
                                "size": 4490,
                                "manipulations": [],
                                "custom_properties": [],
                                "responsive_images": [],
                                "order_column": 1,
                                "created_at": "2024-04-12T09:40:16.000000Z",
                                "updated_at": "2024-04-12T09:40:16.000000Z"
                            }
                        ]
                    }
                ]
            }
        ],
        "author_epitaph_file": None
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(url, json=data, headers=headers) as response:
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

async def main():
    access_token = await get_access_token(MEMORYCODE_EMAIL, MEMORYCODE_PASSWORD)
    if access_token:
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