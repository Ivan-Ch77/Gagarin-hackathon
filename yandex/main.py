import aiohttp
import asyncio


async def post_request(url, headers, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            return await response.text()


async def main():
    catalogID = ""
    secret_key = ""

    prompt = {
        "modelUri": f"gpt://{catalogID}/yandexgpt-lite",
        "completionOptions": {
            "stream": True,
            "temperature": 0.8,
            "maxTokens": "2000",
        },

        # даем пример контекста беседы
        "messages": [
            # system - имитируем систему
            # user - имитируем пользователя
            # assistant - имитируем самого бота, который будет отвечать
            {
                "role": "system",
                "text": "Ты оригинально заполняешь эпиграфию."
            },
            {
                "role": "user",
                "text": "Я заполняю поля в опросе об одном человеке, помоги мне креативно заполнить их."
            },
            {
                "role": "assistant",
                "text": "Привет! Напишите пожалуйста базовую информацию об этом человеке"
            },
            {
                "role": "user",
                "text": "Хорошо, помоги мне на основании этих данных написать эпиграфию."
            },
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {secret_key}"
    }

    # response = requests.post(url, headers=headers, json=prompt)
    # result = response.text

    result = await post_request(url, headers, prompt)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
