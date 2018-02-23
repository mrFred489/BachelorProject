import requests
import random

baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"
baseurl3 = "http://127.0.0.1:5002/"

servers = [baseurl1, baseurl2, baseurl3]

official_url = "https://cryptovoting.dk/"

work_url = baseurl1


def create_addition_secret(x: int, n: int, server_url: str):
    p = get_prime(server_url)
    rng = random.Random()
    res = []
    for i in range(n - 1):
        res.append(rng.randrange(0, p - 1, 1))
    res.append(x - sum(res))
    return res

def create_multiplication_secret(x: int, n: int):
    remaining = x
    rng = random.Random()
    res = []
    for i in range(n-1):
        secret = rng.randrange(0, remaining)
        res.append(secret)
        remaining -= secret
    res.append(remaining)
    return res


def getTotal(urls: list):
    sums = []
    sums_check = []
    for url in urls:
        var = eval(requests.get(url + 'total').text)
        print(url, var)
        sums.append(var)
        sums_check += var
    sums_check = set(sums_check)
    total = 0
    if len(set(sums_check)) == len(urls):
        print("success")
        for name, num in sums_check:
            total += num
    else:
        print("something is wrong")

    print(sums)
    print(sums_check)
    return total % int(get_prime(urls[0] + 'server'))


def get_prime(url: str):
    prime = requests.get(url + '/prime').text
    return int(prime)


def post_url(data: dict, url: str):
    return requests.post(url, data)


def post_secret_to_server(name: list, value: list, url: str):
    return requests.post(url, data=dict(name=name, value=value))


def create_and_post_secret_to_servers(x: int, name: str, servers: list):
    secrets = create_addition_secret(x, len(servers), servers[0])
    names = ["r" + str(i) for i in range(len(secrets))]
    for num, server_url in enumerate(servers):
        # print(requests.post(server_url, data=dict(name=name, value=secrets[num])))
        secrets_c = secrets.copy()
        del secrets_c[num]
        names_c = names.copy()
        del names_c[num]
        print(post_secret_to_server(names_c, secrets_c, server_url))
