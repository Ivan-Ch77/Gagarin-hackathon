

class Text():
    def __init__(self) -> None:
        ...
    
    def start(self):
        text = 'Выберите карточку'
        return text

    def base_info(self):
        text = {
            "full_name": 'Введите ФИО',
            "birthday": 'Введите дату рождения',
            "deathday": 'Введите дату смерти',
            "epitaph": 'Введите эпитафию (надпись на надгробии), можете воспользоваться помощью нейросети',
            "epitaph_author": 'Автор эпитафии',
        }
        return text

    def another_info(self):
        text = {
            "birth_adress": '',
            "death_adress": '',
            "children": '',
            "spouse": '',
            "citizen": '',
        }

    def epitaph_text(self):
        text = 'Давайте напишем биографию вместе, начнем с эпитафии ответьте на пару вопросов'
        question = [
            "Как его звали?",
            "Сколько лет ему было, когда он ушел от нас?",
            "В какой стране и городе он родился?",
            "Какую профессию он имел?",
            "Что он любил делать в свободное время?",
            "Был ли он религиозным человеком?",
            "Имел ли он какие-то особые увлечения/хобби?",
            "Были ли у него особые жизненные принципы или ценности, которые он хотел бы передать своим потомкам?",
            "Был ли он хорошим семьянином?",
            "Каким он был по характеру: добрым, веселым, строгим, спокойным?",
            "Есть ли какие-то особенные истории или моменты, связанные с ним, которые ты хотел бы увековечить в эпитафии?"
        ]
        return {'text':text, 'question':question}

    def biography_main(self):
        text = 'Биография - основа'
        return text 

    def biography_conclusion(self):
        text = 'Биография - заключение'
        return text 

    def friend_words(self):
        text = 'Слова друзей'
        return text 