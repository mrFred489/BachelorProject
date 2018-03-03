from flask import render_template
import numpy as np
import util
import time


def home(db, my_name):
    servers = []
    total = 0
    numbers = db.get_numbers(my_name)
    servers.append({"data": str(numbers)})
    total += sum([x[0] for x in numbers])
    return render_template("server.html", servers=servers, total=total % util.get_prime())


def sum_r_values(votes, servers, server_nr):
    S = [0] * len(servers)
    votes = [x for x in np.asarray(votes) if x[1] == 'r']
    for vote_partition in votes:
        sent_by_server = vote_partition[4] in servers
        if not sent_by_server:
            partition_id = int(vote_partition[2])
            r_i = int(vote_partition[0])
            S[partition_id] += r_i
    for num, val in enumerate(S):
        S[num] = val % util.get_prime()
    return S


def calculate_s(votes, participants):
    used_indexes = []
    s = 0
    s_i_values = [x for x in list(votes) if x[1] == 's']
    if check_received_values(s_i_values, participants):
        for s_i_partition in s_i_values:
            s_i_id = s_i_partition[2]
            s_i = s_i_partition[0]
            if s_i_id not in used_indexes:
                s += int(s_i)
                used_indexes.append(s_i_id)
        return s
    else:
        return 'Database corrupted'


def broadcast_values(values, servers, my_name):
    server_nr = servers.index(my_name)
    for server in servers:
        for num, val in enumerate(values):
            # Only r_i's with i different from server_nr should be sent and not to oneself
            should_be_sent = (num != server_nr) & (server != my_name)
            if should_be_sent:
                send_value_to_server(val, 's', num, my_name, server + "/server")


# Inefficient check of received values
def check_received_values(values, participants):
    is_correct = True
    # amount of participants are the amount of shares a secret is divided into
    for j in range(len(participants)):
        for i in range(len(values)):
            # TODO: find out why x[2] is str
            curr_indexes = [x for x in values if x[2] == j]
            print('CURR_INDEX IS: ' + str(curr_indexes) + ' In round: ' + str(i))
            first_value = curr_indexes[0]
            for value in curr_indexes:
                if value[0] != first_value[0]:
                    is_correct = False
    return is_correct


def send_value_to_server(value, name, id, sender, receiver):
    return util.post_url(data=dict(client=sender, server=sender, name=name, id=id, value=value), url=receiver)
