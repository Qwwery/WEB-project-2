import requests


def get_ip():
    try:
        return requests.get('https://api.ipify.org/?format=json%27').text
    except Exception as e:
        print(e)
        return 'error'
