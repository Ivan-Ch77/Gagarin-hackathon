

class Text():
    def __init__(self) -> None:
        ...
    
    def start(self):
        text = 'Для помощи в написании биографии/эпитафии нажмите <b>Помощь</b>, для создания с нуля нажмите <b>Создать</b>'
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

    def biography_intro(self):
        text = 'Давайте напишем биографию вместе, начнем с вступления ответте на пару вопросов'
        return text 

    def biography_main(self):
        text = 'Биография - основа'
        return text 

    def biography_conclusion(self):
        text = 'Биография - заключение'
        return text 

    def friend_words(self):
        text = 'Слова друзей'
        return text 