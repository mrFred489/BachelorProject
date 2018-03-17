import requests
import random
import util
import scipy.special as ss
import itertools
import pickle
import codecs
import numpy as np
from time import sleep



def create_vote(client_name: str, priorities: list):

### client_name: unique identifier for client
### priorities: list of length #candidates with values ranging from 0 to #candidates-1

### Returns:
### a matrix consisting of rows in which the entries are 0  if the i'th index is different from the value of priorities[i], else 1
    priority_matrix = np.zeros((len(priorities), len(priorities)), dtype=int)
    for num, row in enumerate(priority_matrix):
        row[priorities[num]-1] = 1
    return priority_matrix


def partition_and_secret_share_vote(vote: list, servers: list):
    ###
    r_i_matrices = []
    amount_of_servers = len(servers)
    for i in range(amount_of_servers):
        r_i_matrices.append([])
        for row in vote:
            r_i_matrices[i].append([])
    for i, row in enumerate(vote):
        for value in row:
            curr_secret = util.create_addition_secret(value, amount_of_servers)
            for j, s in enumerate(curr_secret):
                r_i_matrices[j][i].append(s)
    temp = []
    for i in r_i_matrices:
        temp.append(np.array(i))
    return temp


def vote(client_name: str, vote: list, servers: list):
    ### Parameters:
    ### client_name: unique identifier for client
    ### vote: a matrix consisting of matrices containing the different secret shared r_i-elements of the vote
    ### servers: a list with all servers which the secrets should be distributed to

    ### Returns: void. The purpose of the method is to distribute the matrix-shares between clients
    for i, receiving_server in enumerate(servers):
        for j, vote_partition in enumerate(vote):
            if i != j:
                m = dict(client=client_name, id=j, round=1, server=receiving_server,
                         vote=codecs.encode(pickle.dumps(vote_partition), "base64").decode())
                send_vote_partition(m, receiving_server)


def send_vote_partition(message: dict, server_url: str):
    return util.post_url(data=message, url=server_url + 'vote')


def post_secret_to_server(clients: list, servers: list, name: list, id: list, value: list, url: str):
    return util.post_url(data=dict(client=clients, server=servers, name=name, id=id, value=value), url=url + 'server')


def create_arrays_of_servers_to_send_secret_to(n: int, cs=1):
    combs = itertools.combinations(range(0, n), n-cs)
    arrays = []
    for subset in combs:
        arrays.append(list(subset))
    return list(reversed(arrays))


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


def voting_done(servers):
    for server in servers:
        util.get_url(server + 'add')


def calculate_vote_result(servers):
    for server in servers:
        util.post_url(server + 'compute_result')


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
