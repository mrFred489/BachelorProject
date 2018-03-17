import requests
import random
import codecs
import pickle


def get_prime():
    return 50


def post_url(data: dict, url: str):
    return requests.post(url, data)

def get_url(url):
    response = requests.get(url)
    return response


def create_addition_secret(x: int, n: int):
    p = get_prime()
    rng = random.Random()
    res = []
    for i in range(n - 1):
        res.append(rng.randrange(0, p - 1, 1))
    res.append((x - sum(res)) % get_prime())
    return res


def vote_to_string(vote):
    return codecs.encode(pickle.dumps(vote), "base64").decode()


def string_to_vote(string_vote):
    return pickle.loads(codecs.decode(string_vote.encode(), "base64"))