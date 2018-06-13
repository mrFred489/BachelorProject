import requests
import random
import util
import scipy.special as ss
import numpy as np


def send_vote(priorities: list, client_name: str, servers: list):
    vote = create_vote(priorities)
    vote_partitions = util.partition_and_secret_share_vote(vote, servers)
    postvote(client_name, vote_partitions, servers)


def create_vote(priorities: list):

    ### client_name: unique identifier for client
    ### priorities: list of length #candidates with values ranging from 0 to #candidates-1

    ### Returns:
    ### a matrix consisting of rows in which the entries are 0  if the i'th index is different from the value of priorities[i], else 1
    priority_matrix = np.zeros((len(priorities), len(priorities)), dtype=int)
    for num, row in enumerate(priority_matrix):
        row[priorities[num]-1] = 1
    return priority_matrix

def postvote(client_name: str, vote: list, servers: list):
    ### Parameters:
    ### client_name: unique identifier for client
    ### vote: a list consisting of matrices containing the different secret shared r_i-element of the vote
    ### servers: a list with all servers which the secrets should be distributed to
    ###
    ### Returns:
    ### void. Should only distribute secret shares to servers


    for i,share in enumerate(vote):
        rest = vote.copy()
        rest.pop(i)
        ids = [0,1,2,3]
        ids.remove(i)
        rest_strings = []
        for vote_partition in rest:
            rest_strings.append(util.vote_to_string(vote_partition))
        m = dict(client=client_name, ids=ids, server=servers[i], votes=rest_strings, sender=client_name)
        util.get_keys(client_name)
        util.post_url(m, servers[i] + '/vote')

def zero_sum_db_print(servers: list):
    for s in servers:
        util.post_url(data=dict(), url=s + '/z0print')

def get_total(urls: list):
    sums = []
    sums_check = []
    for url in urls:
        var = eval(requests.get(url + '/total').text)
        print("get_total: ", url, var)
        sums.append(var)
        sums_check += var
    sums_check = set(sums_check)
    total = 0
    if len(set(sums_check)) == len(urls):
        print("get_total: ", "success")
        for name, num in sums_check:
            total += num
    else:
        print("get_total: ", "something is wrong")
    return total % int(util.get_prime())


def voting_done(servers):
    for server in servers:
        util.get_url(server + '/add')


def calculate_vote_result(servers):
    for server in servers:
        util.get_url(server + '/compute_result')


def create_multiplication_secret(x: int, n: int, cs=2):
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
