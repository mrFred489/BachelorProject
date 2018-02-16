import requests
import json
import random

def create_secret(x : int, p : int, n : int):
    rng = random.Random()
    res = []
    for i in range(n-1):
        res.append(rng.randrange(0, p-1, 1))
    res.append(x - sum(res))
    return res

def post_url(data : dict, url : str):
    return requests.post(url, data)

def get_url(url : str):
    return requests.get(url)

urltest = "http://127.0.0.1:5000/server1"

data = {'name': 'a', 'value': 5}

print(post_url(data, urltest).text)
