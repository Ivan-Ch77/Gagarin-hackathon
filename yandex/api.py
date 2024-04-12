import aiohttp
from .config import API_KEY_YA, CATALOG_ID

async def fetch_from_yandexgpt(prompt_messages):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {API_KEY_YA}"
    }
    payload = {
        "modelUri": f"gpt://{CATALOG_ID}/yandexgpt3",
        "completionOptions": {
            "stream": False,
            "temperature": 0.8,
            "maxTokens": 2000,
        },
        "messages": prompt_messages
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_message = await response.text()
                return {'error': f'Ошибка API YandexGPT: {response.status}, тело ответа: {error_message}'}
