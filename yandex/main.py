import os
import aiohttp
import asyncio
from dotenv import load_dotenv
import json


async def post_request(url, headers, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            return await response.text()


async def insert_data_into_questions(data):
    num_questions = len(data)
    result = ""
    for i in range(0, num_questions):
        result += f"{i+1}) {data[i]} "
        
    return result.strip()


async def yandexGPT(data):
    load_dotenv()
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
                "text": "Ты оригинально заполняешь эпитафию исходя из данных, которые тебе даст пользователь,"
                        "максимальное количество символов - 300. Нужно составить эпитафию"
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
                "text": await insert_data_into_questions(data)
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
    epigraphies = []
    for line in lines:
        json_obj = json.loads(line)
        if 'result' in json_obj and 'alternatives' in json_obj['result']:
            for alt in json_obj['result']['alternatives']:
                if 'message' in alt and 'text' in alt['message'] and alt['status'] == 'ALTERNATIVE_STATUS_FINAL':
                    text = alt['message']['text']
                    epigraphies.append(text)
    return epigraphies

# if __name__ == "__main__":
#     asyncio.run(yandexGPT())
