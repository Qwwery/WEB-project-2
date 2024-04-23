import requests


def get_setup():
    info = requests.get('https://official-joke-api.appspot.com/random_joke').json()
    setup = info['setup']
    punchline = info['punchline']
    return f'{setup} {punchline}'
