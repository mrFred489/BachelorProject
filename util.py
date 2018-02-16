import requests
import json
import random

baseurl = "http://127.0.0.1:5000/"

def create_secret(x : int, p : int, n : int):
    rng = random.Random()
    res = []
    for i in range(n-1):
        res.append(rng.randrange(0, p-1, 1))
    res.append(x - sum(res))
    return res

def post_url(data : dict, url : str):
    return requests.post(url, data)

def post_secret_to_server(name : str, value : int, serverid):
    return requests.post(baseurl + "/server" + str(serverid), data=dict(name=name, value=value))



print(post_secret_to_server("Christian", 7, 1).text)

print(requests.get(baseurl + "/server" + str(1)).text)

