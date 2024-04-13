from dataclasses import dataclass

@dataclass
class Answer:

    key: str | list[str]
    text: str = ""
    avaliable: bool = False


@dataclass
class Question:
    text: str
    answer: Answer = ''



QUESTIONS = [
    Question(
        text = "Как его звали?",
        answer = Answer(
            key = "name"
        )
    ),
    Question(
        text = "Сколько лет ему было, когда он ушел от нас?",
        answer = Answer(
            key = [
                "birthday_at", 
                "died_at"
            ]
        )
    ),
    Question(
        text="В какой стране и городе он родился?"
    ),
    Question(
        text="Какую профессию он имел?"
    ),
    Question(
        text="Что он любил делать в свободное время?"
    ),
    Question(
        text="Был ли он религиозным человеком?"
    ),
    Question(
        text="Имел ли он какие-то особые увлечения/хобби?"
    ),
    Question(
        text="Были ли у него особые жизненные принципы или ценности, которые он хотел бы передать своим потомкам?"
    ),
    Question(
        text="Был ли он хорошим семьянином?"
    ),
    Question(
        text="Каким он был по характеру: добрым, веселым, строгим, спокойным?"
    ),
    Question(
        text="Есть ли какие-то особенные истории или моменты, связанные с ним, которые ты хотел бы увековечить в эпитафии?"
    )
]


@dataclass
class Field:

    text: str

FIELDS = [
    Field(
        text="ФИО:"
    ),
    Field(
        text="Дата рождения:"
    ),
    Field(
        text="Дата смерти:"
    )
    # Field(
    #     text="Место рождения:"
    # ),
    # Field(
    #     text="Род деятельности:"
    # )
]