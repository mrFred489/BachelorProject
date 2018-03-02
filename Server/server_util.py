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
    votes = np.asarray(votes)
    for vote_partition in votes:
        is_sent_by_server = vote_partition[4] in servers
        if not is_sent_by_server:
            partition_nr = int(vote_partition[2])
            r_i = int(vote_partition[0])
            S[partition_nr] += r_i
    for num, val in enumerate(S):
        S[num] = val % util.get_prime()
    return S


def calculate_s(votes, server_nr):
    used_indexes = []
    s = 0
    votes = np.asarray(votes)
    s_i_values = [x for x in votes if x[1] == 's']
    for s_i_partition in s_i_values:
        s_i_index = s_i_partition[2]
        s_i = s_i_partition[0]
        print('S_'+ s_i_index +' IS: ' + s_i + ' For server ' + s_i_partition[4])
        if s_i_index not in used_indexes:
            print('INDEX ' + str(s_i_index) + ' with value ' + str(s_i) + ' was used for calculation of s')
            s += int(s_i)
            used_indexes.append(s_i_index)
    return s


def broadcast_values(values, servers, my_name):
    server_nr = servers.index(my_name)
    for server in servers:
        for num, val in enumerate(values):
            # Only r_i's with i different from server_nr should be sent
            should_be_sent = num != server_nr
            if (server != my_name) & should_be_sent:
                send_value_to_server(val, 's', num, my_name, server + "/server")


def send_value_to_server(value, name, id, sender, server_url):
    return util.post_url(data=dict(client=sender, server=sender, name=name, id=id, value=value), url=server_url)
