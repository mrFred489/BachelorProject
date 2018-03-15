from flask import render_template
import numpy as np
import util
from operator import mul
from functools import reduce

def home(db, my_name):
    servers = []
    total = 0
    numbers = db.get_numbers(my_name)
    servers.append({"data": str(numbers)})
    total += sum([x[0] for x in numbers])
    return render_template("server.html", servers=servers, total=total % util.get_prime())


def check_row(vote):
    for row in vote:
        if sum(row) != 1:
            return False
    return True


def check_column(vote):
    for i, row in enumerate(vote):
        for j, value in enumerate(row):
            pass


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
            curr_indexes = [x for x in values if x[2] == j]
            if len(curr_indexes) != len(participants)-1:
                print('All values have not yet been received')
                is_correct = False
            first_value = curr_indexes[0]
            for value in curr_indexes:
                if value[0] != first_value[0]:
                    is_correct = False
    return is_correct


def multiply(values, participants: list, my_name: str):
    values = list(values)
    amount_of_servers = len(participants)
    res = [1]*(amount_of_servers)
    client_values = {}

    for vote_partition in values:
        curr_client = vote_partition[3]
        value_index = vote_partition[2]
        value = vote_partition[0]
        if not curr_client in client_values.keys():
            client_values[curr_client] = {}
        client_values[curr_client][str(value_index)] = value
    print(str(client_values))
    server_nr = participants.index(my_name)
    a_i_plus_one = 1
    a_i_plus_two = 1
    for key, client in client_values.items():
        b_i_plus_one = client[str((server_nr+1) % amount_of_servers)]
        b_i_plus_two = client[str((server_nr+2) % amount_of_servers)]
        res[0] *= b_i_plus_one
        res[1] *= a_i_plus_one * b_i_plus_two
        res[2] *= a_i_plus_two * b_i_plus_one
        a_i_plus_one = b_i_plus_one
        a_i_plus_two = b_i_plus_two
    return sum(res)


def sort_values_according_to_client(values):
    client_mapping = {}
    for val in values:
        client = val[4]
        secret = val[0]
        if client not in client_mapping:
            client_mapping[client] = []
        client_mapping[client].append(secret)
    return client_mapping


def send_value_to_server(value, name, id, sender, receiver):
    return util.post_url(data=dict(client=sender, server=sender, name=name, id=id, value=value), url=receiver)
