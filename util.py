import requests
import random


def get_prime():
    return 50


def post_url(data: dict, url: str):
    return requests.post(url, data)

def get_url(url):
    return requests.get(url)


def create_addition_secret(x: int, n: int):
    p = get_prime()
    rng = random.Random()
    res = []
    for i in range(n - 1):
        res.append(rng.randrange(0, p - 1, 1))
    res.append(int((x - sum(res)) % get_prime()))
    return res
