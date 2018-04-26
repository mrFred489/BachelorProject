import numpy as np
import util
from collections import defaultdict


def broadcast(data, servers, url):
    for server in servers:
        data["server"] = server
        send_value_to_server(data, server + url)


def list_remove(l:list, element):
    temp = l.copy()
    del temp[l.index(element)]
    return temp


def check_rows_and_columns(vote: np.ndarray):  # slet
    for row in vote:
        if np.sum(row) != 1:
            return False
    for col in vote.T:
        if np.sum(col) != 1:
            return False
    return True


def create_sum_of_row(vote):  # slet
    res = []
    for row in vote:
        res.append(np.sum(row))
    return np.array(res)


def broadcast_rows_and_cols(row, col, id_, servers, my_name, client_name):  # slet
    servers = list_remove(servers, my_name)
    broadcast(dict(vote=(util.vote_to_string(row)),
                              id=id_, round="row",
                              server=my_name,
                              client=client_name),
              servers, '/server_comm')

    broadcast(dict(vote=(util.vote_to_string(col)),
                              id=id_, round="column",
                              server=my_name,
                              client=client_name),
              servers, '/server_comm')


def broadcast_values(values, round_, servers, my_name):
    servers = list_remove(servers, my_name)
    for j, vote_partition in enumerate(values):
            broadcast(dict(vote=(util.vote_to_string(vote_partition['vote_partition'])),
                              id=vote_partition["id"], round=round_,
                              server=my_name,
                              client=my_name),
                      servers, '/submit')

def broadcast_illegal_votes(clients, my_name, servers):
    servers = list_remove(servers, my_name)
    broadcast({'clients': clients, 'server': my_name}, servers, '/illegal')


def secret_share(votes, servers):
    ss_votes = []
    for vote in votes:
        ss_vote = util.partition_and_secret_share_vote(vote['vote_partition'], servers)
        ss_votes.append(ss_vote)
    return ss_votes


def sum_votes(votes):
    summed_votes = []
    for vote in votes:
        vote_id = vote[1]
        vote_partition = vote[0]
        if len([x for x in summed_votes if x['id'] == vote_id]) > 0:
            for dict in summed_votes:
                if dict['id'] == vote_id:
                    acc = dict['vote_partition']
                    dict['vote_partition'] = np.add(vote_partition, acc)
        else:
            summed_votes.append({'vote_partition': vote_partition, 'id': vote_id})
    return summed_votes


def send_value_to_server(data, url):
    return util.post_url(data=data, url=url)


def verify_consistency(votes):
    votes_sorted = sorted(votes, key=lambda x: x[1])
    prev = votes_sorted[0]
    for vote in votes_sorted:
        if vote[1] == prev[1] and not np.array_equal(vote[0], prev[0]):
            print("not equal", vote, prev)
            return False
        prev = vote
    return True


def verify_sums(rows):
    illegal_votes = set()
    sorted(rows, key=lambda x: x[3])
    diff_clients = []
    for x in rows:
        if x[3] not in diff_clients:
            diff_clients.append(x[3])
    for client in diff_clients:
        client_rows = [x for x in rows if x[3] == client]
        if verify_consistency(client_rows):
            res = 0
            used_rows = []
            for row in client_rows:
                row_id = row[1]
                if row_id not in used_rows:
                    used_rows.append(row_id)
                    res += row[0]
            sums = res % util.get_prime()
            for sum in sums:
                if (sum != 1) & (client not in illegal_votes):
                    illegal_votes.add(client)
    return illegal_votes


def calculate_result(votes, illegal_votes):
    used_votes = []
    res = 0
    for vote in votes:
        vote_id = vote[1]
        round = vote[2]
        client_name = vote[3]
        if (vote_id not in used_votes) & (round == 2):
            used_votes.append(vote_id)
            res += vote[0]
    res = res
    return res % util.get_prime()


def to_mult(id, num_servers):
    cs = int(num_servers/2)
    res = []
    res.append(((id + cs) % num_servers, (id + cs) % num_servers))
    for i in range(int(num_servers/2)):
        res.append(((id + cs) % num_servers, (id + cs + 1 + i) % num_servers))
        res.append(((id + cs + 1 + i) % num_servers, (id + cs) % num_servers))
    return res

def index_zero_one_check(id, num_servers, xs):
    new_val = 0
    for (i, j) in to_mult(id, num_servers):
        xi = xs[i]
        xj = (xs[j]-(1/num_servers))
        new_val += (xi * xj)
    return new_val

def matrix_zero_one_check(id, num_servers, xs):
    # xs = dict: (id) => x_i
    new_matrix = np.zeros(list(xs.values())[0].shape)
    for i in range(new_matrix.shape[0]):
        for j in range(new_matrix.shape[1]):
            index_dict = dict()
            for ind, matrix in xs.items():
                index_dict[ind] = matrix[i][j]
            new_matrix[i][j] = index_zero_one_check(id, num_servers, index_dict)
    return new_matrix

def zero_one_check(xs):
    res = sum(xs)
    return np.rint(res) % util.get_prime()


def zero_one_illegal_check(values):
    # values = [(matrix, client, server), ...]
    # print(values)
    zerocheck_secrets = defaultdict(list)

    for check in values:
        zerocheck_secrets[check[1]].append(check[0])

    illegal_votes = set()
    for key in zerocheck_secrets.keys():
        # print(zero_one_check(zerocheck_secrets[key]))
        if not np.array_equal(zero_one_check(zerocheck_secrets[key]),np.zeros(zerocheck_secrets[key][0].shape)):
            illegal_votes.add(key)

    return illegal_votes
