# pip install install googletrans==3.1.0a0
import requests
from googletrans import Translator


def translate(setup, punchline):
    translator = Translator()
    try:
        setup_translate = translator.translate(text=setup, src='en', dest='ru')
        setup_translate = setup_translate.text
        punchline_translate = translator.translate(text=punchline, src='en', dest='ru')
        punchline_translate = punchline_translate.text
        return setup_translate, punchline_translate
    except Exception as e:
        print(e)
        return setup, punchline


def get_setup():
    info = requests.get('https://official-joke-api.appspot.com/random_joke').json()
    setup = info['setup']
    punchline = info['punchline']

    setup, punchline = translate(setup, punchline)
    return f'{setup} {punchline}'
