import requests
import json
import random

baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"
baseurl3 = "http://127.0.0.1:5002/"

servers = [baseurl1, baseurl2, baseurl3]

official_url = "https://cryptovoting.dk/"

work_url = baseurl1


def create_secret(x: int, n: int, server_url: str):
    p = get_prime(server_url)
    rng = random.Random()
    res = []
    for i in range(n - 1):
        res.append(rng.randrange(0, p - 1, 1))
    res.append(x - sum(res))
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


# Sieve of Eratosthenes
# Code by David Eppstein, UC Irvine, 28 Feb 2002
# http://code.activestate.com/recipes/117119/

def gen_primes():
    """ Generate an infinite sequence of prime numbers.
    """
    # Maps composites to primes witnessing their compositeness.
    # This is memory efficient, as the sieve is not "run forward"
    # indefinitely, but only as long as required by the current
    # number being tested.
    #
    D = {}

    # The running integer that's checked for primeness
    q = 2

    while True:
        if q not in D:
            # q is a new prime.
            # Yield it and mark its first multiple that isn't
            # already marked in previous iterations
            #
            yield q
            D[q * q] = [q]
        else:
            # q is composite. D[q] is the list of primes that
            # divide it. Since we've reached q, we no longer
            # need it in the map, but we'll mark the next
            # multiples of its witnesses to prepare for larger
            # numbers
            #
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]

        q += 1


primes = gen_primes()


def get_prime(url: str):
    prime = requests.get(url + '/prime').text
    return int(prime)


def post_url(data: dict, url: str):
    return requests.post(url, data)


def post_secret_to_server(name: list, value: list, url: str):
    return requests.post(url, data=dict(name=name, value=value))


def create_and_post_secret_to_servers(x: int, name: str, servers: list):
    secrets = create_secret(x, len(servers), servers[0])
    names = ["r" + str(i) for i in range(len(secrets))]
    for num, server_url in enumerate(servers):
        # print(requests.post(server_url, data=dict(name=name, value=secrets[num])))
        secrets_c = secrets.copy()
        del secrets_c[num]
        names_c = names.copy()
        del names_c[num]
        print(post_secret_to_server(names_c, secrets_c, server_url))

# post_url(url=baseurl1 + "server", data={"name": ["a", "b", "c"], "value": [1,2,3]})


# for num in primes:
#     if num >= 4000001:
#         print(num)
#         break
