import requests
import random
import util
import scipy.special as ss
import itertools


def create_addition_secret(x: int, n: int, server_url: str):
    p = util.get_prime()
    rng = random.Random()
    res = []
    for i in range(n - 1):
        res.append(rng.randrange(0, p - 1, 1))
    res.append(x - sum(res))
    return res


def create_multiplication_secret(x: int, n: int, cs=1):
    remaining = x
    rng = random.Random()
    res = []
    n = ss.binom(n, cs)
    for i in range(int(n) - 1):
        secret = rng.randrange(0, remaining)
        res.append(secret)
        remaining -= secret
    res.append(remaining)
    return res


def create_arrays_of_servers_to_send_secret_to(n: int, cs: int):
    combs = itertools.combinations(range(1, n + 1), cs)
    arrays = []
    for subset in combs:
        arrays.append(list(subset))
    return arrays


def post_multiplication_secrets_to_servers(url: str, xs, arrays, name: str, client: str):
    lenx = len(xs)
    lenarrays = len(arrays)
    if (lenarrays != lenx):
        return
    for xi in range(lenx):
        for ser in arrays[xi]:
            post_url(dict(client=client, server=client, name=name, id=str(xi), value=xs[xi]), url + str(ser))


def get_total(urls: list):
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


def post_secret_to_server(clients: list, servers: list, name: list, id: list, value: list, url: str):
    return util.post_url(data=dict(client=clients, server=servers, name=name, id=id, value=value), url=url)


def create_and_post_secret_to_servers(x: int, name: str, servers: list):
    secrets = create_addition_secret(x, len(servers), servers[0])
    names = ["r" for i in range(len(secrets))]
    id = [str(i) for i in range(len(secrets))]
    clients = [name] * (len(secrets) - 1)
    for num, server_url in enumerate(servers):
        secrets_c = secrets.copy()
        del secrets_c[num]
        names_c = names.copy()
        del names_c[num]
        id_c = id.copy()
        del id_c[num]
        post_secret_to_server(clients, clients, names_c, id_c, secrets_c, server_url)
