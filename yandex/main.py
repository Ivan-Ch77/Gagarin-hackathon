import os
import aiohttp
import asyncio
from dotenv import load_dotenv
import json
import re

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
    SECRET_KEY = os.getenv('API_KEY_YA')


    prompt = {
        "modelUri": f"gpt://{CATALOG_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": True,
            "temperature": 0.9,
            "maxTokens": "1000",
        },

        # даем пример контекста беседы
        "messages": [
            # system - контекст запроса, определяющий поведение модели
            # user - имитируем пользователя
            # assistant - имитируем самого бота, который будет отвечать
            {
                "role": "system",
                "text": "Составь только одну эпиграфию длиной до 300 символов. Выдели ее символами « »"
                        # "Используй эти символы «» ТОЛЬКО для того, чтобы выделять текст эпитафии."
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
    # TODO: на данный момент не выходит грамотно разделить ответ на 3 эпитафии/биографии
    lines = result.strip().split('\n')
    epigraphies = []
    for line in lines:
        json_obj = json.loads(line)
        if 'result' in json_obj and 'alternatives' in json_obj['result']:
            for alt in json_obj['result']['alternatives']:
                if 'message' in alt and 'text' in alt['message'] and alt['status'] == 'ALTERNATIVE_STATUS_FINAL':
                    text = alt['message']['text']
                    print(text)
                    print('---------------------------------')
                    positions1 = [match.start() for match in re.finditer('«', text)]
                    positions2 = [match.start() for match in re.finditer('»', text)]
                    print(positions1, positions2)
                    for pos in range(len(positions1)):
                        epigraphies.append(text[positions1[pos-1]:positions2[pos]])

    return epigraphies

if __name__ == "__main__":
    # data = [
    #     "Ответ на первый вопрос", "Ответ на второй вопрос", "Россия, Москва","Он был сварщиком",
    #     "Он любил читать книги и рисовать", "Да, он был религиозным человеком", "Особенным его хобби было рисовать утренний рассвет",
    #     "Нет", "Да", "Он был добрым, но строгим", "Нет."
    # ]
    data = [
        'Андрей Антоныч', '65', 'Россия, Москва', 'Он был инженером', 'Он любил петь', 'Нет', 'Да',
        'Он был очень целеустремленным', 'Да', 'Он был скромным', 'нет'
    ]
    # asyncio.run(yandexGPT(data))
    result1 = asyncio.run(yandexGPT(data))
    print('\n\n')
    # for i in range(len(result1)):
    #     print(result1[i], '\n\n')
    ss = 'Здесь лежит Андрей Антоныч. Инженер, певец и просто замечательный человек. Жил с 1957 по 2033 год. Прожил долгую и насыщенную жизнь. Навеки в наших сердцах'
    sum=0
    for i in range(len(ss)):
        sum +=1
    print(sum)

