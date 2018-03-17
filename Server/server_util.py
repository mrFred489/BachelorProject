from flask import render_template
import numpy as np
import util
from operator import mul
from functools import reduce
import pickle
import codecs


def home(db, my_name):
    servers = []
    total = 0
    numbers = db.get_numbers(my_name)
    servers.append({"data": str(numbers)})
    total += sum([x[0] for x in numbers])
    return render_template("server.html", servers=servers, total=total % util.get_prime())


def check_rows_and_columns(vote: np.ndarray):
    for row in vote:
        if sum(row) != 1:
            return False
    for col in vote.T:
        if sum(col) != 1:
            return False
    return True


def broadcast_values(values, servers, my_name):
    server_nr = servers.index(my_name)
    for i, server in enumerate(servers):
        if i != server_nr:
            for j, vote_partition in enumerate(values):
                # print("Broadcasted value is: ", vote_partition['vote_partition'], " with ID: ", vote_partition['id'])
                send_value_to_server(
                    (codecs.encode(pickle.dumps(vote_partition['vote_partition']), "base64").decode()),
                    vote_partition['id'], 2, my_name, server)


def reshape_vote(vote):
    shape = int(np.sqrt(len(vote)))
    return np.reshape(vote, (shape, shape))


def sum_votes(votes, servers, my_name):
    summed_votes = []
    for vote in votes:
        vote_id = vote[1]
        # TODO: It seems that the votes retrieved from the database sometimes are changed to values very close to zero,
        # find out why. I believe it happens when the values are saved to the database.
        # They look fine when being received, but when retrieved for use in sum_votes, some matrices consist of values close to zero
        vote_partition = reshape_vote(vote[0])
        if len([x for x in summed_votes if x['id'] == vote_id]) > 0:
            for dict in summed_votes:
                if dict['id'] == vote_id:
                    acc = dict['vote_partition']
                    dict['vote_partition'] = np.add(vote_partition, acc)
        else:
            summed_votes.append({'vote_partition': vote_partition, 'id': vote_id})
    return summed_votes


def send_value_to_server(value, id,  round, sender, receiver):
    return util.post_url(data=dict(client=sender, server=sender, vote=value, id=id, round=round), url=receiver + '/vote')


def verify_vote_consistency(votes):
    votes_sorted = sorted(votes, key=lambda x: x[1])
    prev = votes_sorted[0]
    for vote in votes_sorted:
        if vote[1] == prev[1] and not np.array_equal(vote[0], prev[0]):
            print("not equal", vote, prev)
            return False
        prev = vote
    return True


def calculate_s(votes, participants):
    used_votes = []
    res = 0
    for vote in votes:
        round = vote[2]
        vote_id = vote[1]
        if (vote_id not in used_votes) & (round == 2):
            used_votes.append(vote_id)
            res += vote[0]
    print("S IS: ", reshape_vote(res % util.get_prime()))
    print("Result consists of :", used_votes, " votes put together ")
    return res % util.get_prime()


# def sum_r_values(votes, servers, server_nr):
#     S = [0] * len(servers)
#     votes = [x for x in np.asarray(votes) if x[2] == 1]
#     for vote_partition in votes:
#         sent_by_server = vote_partition[4] in servers
#         if not sent_by_server:
#             partition_id = int(vote_partition[2])
#             r_i = int(vote_partition[0])
#             S[partition_id] += r_i
#     for num, val in enumerate(S):
#         S[num] = val % util.get_prime()
#     return S


# def sort_values_according_to_client(values):
#     client_mapping = {}
#     for val in values:
#         client = val[4]
#         secret = val[0]
#         if client not in client_mapping:
#             client_mapping[client] = []
#         client_mapping[client].append(secret)
#     return client_mapping



















