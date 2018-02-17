import requests
import json
import random

baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"

def create_secret(x : int, p : int, n : int):
    rng = random.Random()
    res = []
    for i in range(n-1):
        res.append(rng.randrange(0, p-1, 1))
    res.append(x - sum(res))
    return res


def post_url(data: dict, url: str):
    return requests.post(url, data)


def post_secret_to_server(name : str, value : int, serverid : int):
    return requests.post(baseurl1 + "server" + str(serverid), data=dict(name=name, value=value))


def create_and_post_secret_to_servers(x: int, p: int, name: str, servers: list):
    secrets = create_secret(x, p, len(servers))
    for num, server_url in enumerate(servers):
        print(requests.post(server_url, data=dict(name=name, value=secrets[num])))


def test_multiple_servers():
    # Husk at starte to servere, med hver deres port nummer.
    servers = [baseurl1 + "server0", baseurl2 + "server0"]
    create_and_post_secret_to_servers(28, 100, "x", servers)
    create_and_post_secret_to_servers(22, 100, "x", servers)

    num1 = requests.get(baseurl1).text
    num2 = requests.get(baseurl2).text

    print(num1, "+", num2, "=", int(num1) + int(num2))
    print("database1:", requests.get(baseurl1 + "databases").text)
    print("database2:", requests.get(baseurl2 + "databases").text)


x = create_secret(22, 100, 3)
y = create_secret(28, 100, 3)

for i in range(len(x)):
    print(post_secret_to_server("x", x[i], i))
    print(post_secret_to_server("y", y[i], i))

print(requests.get(baseurl1).text)
print(requests.get(baseurl1 + "databases").text)





