from flask import render_template
import numpy as np
import util
from Server import database as db


def check_rows_and_columns(vote: np.ndarray):
    for row in vote:
        if sum(row) != 1:
            return False
    for col in vote.T:
        if sum(col) != 1:
            return False
    return True


def broadcast_values(values, round, servers, my_name):
    server_nr = servers.index(my_name)
    for i, server in enumerate(servers):
        for j, vote_partition in enumerate(values):
            if i != server_nr:
                send_value_to_server(
                    (util.vote_to_string(vote_partition['vote_partition'])),
                    vote_partition['id'], round, my_name, server)


def reshape_vote(vote):
    shape = int(np.sqrt(len(vote)))
    return np.reshape(vote, (shape, shape))


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
    return util.post_url(data=dict(client=sender, server=sender, vote=value, id=id, round=round), url=receiver + '/submit')


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
        vote_id = vote[1]
        round = vote[2]
        if (vote_id not in used_votes) & (round == 2):
            used_votes.append(vote_id)
            res += vote[0]
    res = reshape_vote(res)
    return res % util.get_prime()



















