import requests
import json
import random

baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"

official_url = "https://cryptovoting.dk/"

work_url = baseurl1

def create_secret(x : int, n : int, server_url: str):
    p = get_prime(server_url)
    rng = random.Random()
    res = []
    for i in range(n-1):
        res.append(rng.randrange(0, p-1, 1))
    res.append(x - sum(res))
    return res

def getTotal(urls: list):
    sum = 0
    for url in urls:
        var = requests.get(url + 'total').text
        print(var)
        sum += int(var)
    return sum % int(get_prime(urls[0] + 'server1'))

def get_prime(url: str):
    print(url)
    prime = requests.get(url + '/prime').text
    print(prime)
    return int(prime)


def post_url(data: dict, url: str):
    return requests.post(url, data)


def post_secret_to_server(name: str, value: int,  url: str):
    return requests.post(url, data=dict(name=name, value=value))


def create_and_post_secret_to_servers(x: int, p: int, name: str, servers: list):
    secrets = create_secret(x, len(servers), servers[0])
    for num, server_url in enumerate(servers):
        # print(requests.post(server_url, data=dict(name=name, value=secrets[num])))
        print(post_secret_to_server(name, secrets[num], server_url))






