import requests


def get_prime():
    return 4000037


def post_url(data: dict, url: str):
    return requests.post(url, data)
