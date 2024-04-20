import asyncio
import sys
from g4f.client import Client

if sys.platform == 'win64':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_synonyms(word: str):
    client = Client(metaclass=Singleton)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Напиши синонимы слову {word} в виде строки разделяя запятой и не пиши ничего лишнего"}],
    )
    return response.choices[0].message.content.split(', ')


def get_antonyms(word: str):
    client = Client(metaclass=Singleton)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Напиши антонимы слову {word} в виде строки разделяя запятой и не пиши ничего лишнего"}],
    )
    return response.choices[0].message.content.split(', ')


def chatting(message: str):
    client = Client(metaclass=Singleton)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"{message}"}],
    )
    return response.choices[0].message.content
