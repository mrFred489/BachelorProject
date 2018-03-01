import requests
import random
import util
import scipy.special as ss
import itertools
baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"
baseurl3 = "http://127.0.0.1:5002/"

servers = [baseurl1, baseurl2, baseurl3]

official_url = "https://cryptovoting.dk/"

work_url = baseurl1


def create_addition_secret(x: int, n: int, server_url: str):
    p = util.get_prime()
    rng = random.Random()
    res = []
    for i in range(n - 1):
        res.append(rng.randrange(0, p - 1, 1))
    res.append(x - sum(res))
    return res


def create_multiplication_secret(x: int, n: int, cs: int):
    remaining = x
    rng = random.Random()
    res = []
    n = ss.binom(n, cs)
    for i in range(int(n)-1):
        secret = rng.randrange(0, remaining)
        res.append(secret)
        remaining -= secret
    res.append(remaining)
    return res

def create_arrays_of_multiplication_secrets_to_send(x, n: int, cs: int):
    combs = itertools.combinations(range(1, 8), 3)
    arrays = []
    for subset in combs:
        arrays.append([].append(subset))
    return arrays

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
    return total % int(util.get_prime())


def post_url(data: dict, url: str):
    return requests.post(url, data)


def post_secret_to_server(clients: list, servers: list, name: list, value: list, url: str):
    return requests.post(url, data=dict(client=clients, server=servers, name=name, value=value))


def create_and_post_secret_to_servers(x: int, name: str, servers: list):
    secrets = create_addition_secret(x, len(servers), servers[0])
    clients = [name] * (len(secrets) - 1)
    names = ["r" + str(i) for i in range(len(secrets))]
    for num, server_url in enumerate(servers):
        secrets_c = secrets.copy()
        del secrets_c[num]
        names_c = names.copy()
        del names_c[num]
        post_secret_to_server(clients, clients, names_c, secrets_c, server_url)
