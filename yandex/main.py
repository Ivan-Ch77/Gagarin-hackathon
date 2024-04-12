import os
import aiohttp
import asyncio
from dotenv import load_dotenv
import json


load_dotenv()


async def post_request(url, headers, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            return await response.text()


async def main():
    CATALOG_ID = os.getenv('CATALOG_ID')
    SECRET_KEY = os.getenv('SECRET_KEY')


    prompt = {
        "modelUri": f"gpt://{CATALOG_ID}/yandexgpt-lite",
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
                "text": "Ты оригинально заполняешь эпиграфию исходя из данных, которые тебе даст пользователь,"
                        "максимальное количество символов - 300. Нужно составить 3 эпиграфии, чтобы пользователь"
                        "мог выбрать подходящую."
            },
            {
                "role": "user",
                "text": "Я заполняю поля в опросе об одном человеке, помоги мне креативно заполнить их."
            },
            {
                "role": "assistant",
                "text": "Привет! Конечно, ответь пожалуйста на эти вопросы:"
                        "1) Какое у него было имя?"
                        "2) Сколько лет ему было, когда он ушел от нас?"
                        "3) В какой стране и городе он родился?"
                        "4) Какую профессию он имел?"
                        "5) Что он любил делать в свободное время?"
                        "6) Был ли он религиозным человеком?"
                        "7) Имел ли он какие-то особые увлечения/хобби?"
                        "8) Были ли у него особые жизненные принципы или ценности, которые он хотел бы передать своим потомкам?"
                        "9) Был ли он хорошим семьянином?"
                        "10) Каким он был по характеру: добрым, веселым, строгим, спокойным?"
                        "11) Есть ли какие-то особенные истории или моменты, связанные с ним, которые ты хотел бы увековечить в эпитафии?"
            },
            {
                "role": "user",
                "text": "1) Алексей 2) 65 3) Россия, Москва 4)Он был сварщиком 5) Он любил читать книги и рисовать"
                        "6) Да, он был религиозным человеком 7) Особенным его хобби было рисовать утренний рассвет"
                        "8) Нет 9) Да 10) Он был добрым, но строгим 11) нет."
            },
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {SECRET_KEY}"
    }

    # response = requests.post(url, headers=headers, json=prompt)
    # result = response.text

    result = await post_request(url, headers, prompt)
    lines = result.strip().split('\n')

    for line in lines:
        json_obj = json.loads(line)
        if 'result' in json_obj and 'alternatives' in json_obj['result']:
            for alt in json_obj['result']['alternatives']:
                if 'message' in alt and 'text' in alt['message'] and alt['status']=='ALTERNATIVE_STATUS_FINAL':
                    text = alt['message']['text']
                    print(text)

if __name__ == "__main__":
    asyncio.run(main())
