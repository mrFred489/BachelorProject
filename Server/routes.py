#!/usr/bin/env python3
from flask import Flask, request, Response, make_response
from Server import database as db
from Server import server_util
from Server import cheat_util
import util
import sys
import numpy as np
import logging
import math
import os.path
from collections import defaultdict



app = Flask(__name__)
app.url_map.strict_slashes = False
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# numbers = defaultdict(list)
testing = False  # variabel til at s(lå database fra hvis vi kører det lokalt

try:
    my_name = str(os.path.dirname(__file__).split("/")[3])
except:
    my_name = "test"


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


global servers

test_servers = [
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003"
]

test_mediator = "http://127.0.0.1:5100"

official_servers = [
    "https://cryptovoting.dk/",
    "https://server1.cryptovoting.dk/",
    "https://server2.cryptovoting.dk/",
    "https://server3.cryptovoting.dk/",
    # "https://server4.cryptovoting.dk/"
]

cheating = False
cheating_nums = []
cheat_id = 0

if not testing:
    servers = test_servers
    mediator = test_mediator
else:
    servers = official_servers

found_malicious_server = False
malicious_server = ""
communication_number: int = 0


@app.route("/reset", methods=["POST"])
def reset():
    db.reset(my_name)
    return Response(status=200)


@app.route("/vote", methods=["POST"])
def vote():
    global communication_number
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    try:
        # Unpack data
        votes_ = data['votes']
        if type(votes_) == str:
            votes_ = [votes_]
        ids_ = data['ids']
        if type(ids_) in [str, int]:
            ids_ = [ids_]
        server_name = data['server']
        client = data['client']

        # Convert votes_ to list of np.array
        votes = []
        for num, v_ in enumerate(votes_):
            if num in cheating_nums and cheat_id == 1:
                print ("vote: cheating")
                votes.append(cheat_util.col_row_cheat(util.string_to_vote(v_)))
                print ("vote: ", votes[-1])
            else:
                votes.append(util.string_to_vote(v_))

        # Attach each share to its proper id
        id_vote_tuple = list(zip(ids_, votes))

        # Insert votes, row and column in db and broadcast
        for (id, vote) in id_vote_tuple:
            row_sum = server_util.create_sum_of_row(vote)
            col_sum = server_util.create_sum_of_row(vote.T)

            db.insert_vote(vote, id, 1, client, server_name, my_name)

            db.insert_row(row_sum, id, 'row', client, server_name, my_name)
            db.insert_col(col_sum, id, 'column', client, server_name, my_name)

            server_util.broadcast_rows_and_cols(row_sum, col_sum, id, servers, my_name, client)

        # Insert zero check and broadcast
        my_id = servers.index(my_name)

        votes_dict = dict()
        for id, v in id_vote_tuple:
            votes_dict[id] = v

        local_parts, communcations = server_util.matrix_zero_one_check(my_id, servers, votes_dict, my_name, client)
        communication_number += communcations
        for local_part in local_parts:
            for x, ss in enumerate(local_part[3]):
                db.insert_zero_partition(matrix=ss, x=x, i=local_part[1], j=local_part[2], client_name=local_part[5], server=my_name, db_name=my_name)
    except TypeError as e:
        print("vote", e)
        return Response(status=400)
    return Response(status=200)


@app.route("/server_comm", methods=["POST"])
def receive_broadcasted_value():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    vote_ = data['vote']
    vote = util.string_to_vote(vote_)
    assert type(vote) == np.ndarray
    id_ = data['id']
    type_ = data['round']
    client = data['client']
    server_name = data['server']
    if type_ == 'row':
        db.insert_row(vote, id_, type_, client, server_name, my_name)
    elif type_ == 'column':
        db.insert_col(vote, id_, type_, client, server_name, my_name)
    return Response(status=200)


@app.route("/zerocheck", methods=["POST"])
def zerocheck():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    try:
        vote_ = data['vote']
        vote = util.string_to_vote(vote_)
        assert type(vote) == np.ndarray
        client = data['client']
        server_name = data['server']
        db.insert_zero_check(vote, client, server_name, my_name)

    except TypeError as e:
        print("zerocheck: ", vote_)
        print("zerocheck: ", e)
        return Response(status=400)

    return Response(status=200)


@app.route("/zeroonepartitions", methods=["POST"])
def zeroonepartions():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    try:
        partitions_ = data['ss']
        partitions_ = [(x, util.string_to_vote(y)) for (x,y) in partitions_]
        i_ = data['i']
        j_ = data['j']
        server_ = data['server']
        id_ = data['id']
        client_ = data['client']
        for x, ss in partitions_:
            db.insert_zero_partition(ss, x, i_, j_, client_, server_, my_name)
    except TypeError as e:
        print("zeroonepartitions: ", data)
        print("zeroonepartitions: ", e)
        return Response(status=400)

    return Response(status=200)


@app.route("/check_votes", methods=["GET"])
def check_votes():
    global communication_number

    # COLUMN ROW CHECK
    cols = db.get_cols(my_name)
    rows = db.get_rows(my_name)
    
    illegal_votes = set(server_util.verify_sums(rows, my_name))
    illegal_votes = illegal_votes.union(server_util.verify_sums(cols, my_name))

    zero_one_illegal_votes = zeroone_sum_partition_finalize()

    illegal_votes = illegal_votes.union(zero_one_illegal_votes)

    # TODO: Ensure agreement among servers regarding illegal_votes

    list_illegal_votes = list(illegal_votes)




    # Save own illegal votes
    db.insert_illegal_votes(list_illegal_votes, my_name, my_name)

    # Broadcast own illegal votes to others
    server_util.broadcast_illegal_votes(list_illegal_votes, my_name, servers)
    communication_number += 3
    return Response(status=200)


@app.route("/zero_one_consistency", methods=["GET"])
def zero_one_partitions_consistency_check():  # Create differences for secret shared values, sum later
    # Create three dimensional list which contains lists for each share of a part of a product

    global communication_number
    partition_dict = db.get_zero_partitions(my_name)
    partition_dict_clients = partition_dict.keys()
    for client in partition_dict_clients:
        partition_matrix_list = [[[[] for h in range(len(servers))] for j in range(len(servers))] for i in range(len(servers))]
        for partition in partition_dict[client]:
            partition_matrix_list[partition['i']][partition['j']][partition['x']].append((partition['matrix'],partition['server']))

        # Ensure that two should-be-identical parts from different servers are, indeed, identical, that a - b = 0.
        datas = []
        for i in range(len(servers)):
            for j in range(len(servers)):
                for x in range(len(servers)):
                    matrix_server_pairs = enumerate(partition_matrix_list[i][j][x])
                    for y, (matrix_y, server_y) in matrix_server_pairs:
                        for z, (matrix_z, server_z) in matrix_server_pairs:
                            if(y < z):
                                difference = np.subtract(np.array(matrix_y), np.array(matrix_z))
                                # broadcast_difference_share
                                datas.append(
                                    dict(diff=util.vote_to_string(difference),
                                         x=x, i=i, j=j, server_a=server_y, server_b=server_z,
                                         server=my_name, client=client))
                                db.insert_zero_consistency_check(
                                    diff=difference, x=x, i=i, j=j,
                                    server_a=server_y, server_b=server_z,
                                    server=my_name, client_name=client, db_name=my_name)
        communication_number += 3
        server_util.broadcast(data=dict(datas=datas, server=my_name), servers=servers, url="/differenceshareforzeroone")
    return Response(status=200)


@app.route("/differenceshareforzeroone", methods=["POST"])
def differenceshareforzeroone():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    try:
        datas_ = data['datas']
        for data_ in datas_:
            diff_ = data_['diff']
            diff_ = util.string_to_vote(diff_)
            x_ = data_['x']
            i_ = data_['i']
            j_ = data_['j']
            server_a_ = data_['server_a']
            server_b_ = data_['server_b']
            client_ = data_['client']
            server_ = data_['server']

            # Save each difference in database
            db.insert_zero_consistency_check(diff=diff_, x=x_, i=i_, j=j_, server_a=server_a_, server_b=server_b_, client_name=client_, server=server_, db_name=my_name)
    except TypeError as e:
        print("differenceshareforzeroone: ", e)
        return Response(status=400)
    return Response(status=200)


@app.route("/sumdifferenceshareforzeroone", methods=["GET"])
def sumdifferenceshareforzeroone():  # Verify servers have calculated the same
    difference_dict = db.get_zero_consistency_check(my_name)
    difference_dict_clients = difference_dict.keys()
    disagreed_clients = []
    for client in difference_dict_clients:
        difference_matrix_list = [[[[] for h in range(len(servers))] for j in range(len(servers))] for i in range(len(servers))]
        for difference in difference_dict[client]:
            difference_matrix_list[difference['i']][difference['j']][difference['x']].append((difference['diff'],difference['server_a'], difference['server_b'], difference['server']))

        # Ensure diff_a = diff_b and sum diff_shares
        result = [[0 for j in range(len(servers))] for i in range(len(servers))]
        for i in range(len(servers)):
            for j in range(len(servers)):
                res = []
                server_difference_dict = defaultdict(list)
                server_difference_x_dict = defaultdict(list)
                for x in range(len(servers)):
                    differences = difference_matrix_list[i][j][x]
                    for difference in differences:
                        server_difference_dict[difference[1] + ":" + difference[2]].append((difference[0], x, difference[3], difference))
                        server_difference_x_dict[difference[1] + difference[2] + str(x)].append((difference[0], difference[3]))

                # SERVER PARTITION TESTS
                server_difference_x_keys = server_difference_x_dict.keys()
                for key in server_difference_x_keys:
                    first_x_diff = server_difference_x_dict[key][0][0]
                    first_x_server = server_difference_x_dict[key][0][1]
                    diff_x_tuple_set = server_difference_x_dict[key][1:]
                    for diff_x_tuple in diff_x_tuple_set:
                        diff_x = diff_x_tuple[0]
                        server_x = diff_x_tuple[1]
                        if not np.array_equal(first_x_diff, first_x_diff):
                            # Disagreement in diff partitions
                            print("sumdifferenceshareforzeroone: ", "Disagreement in difference partitions")


                # DIFF TESTS
                server_difference_keys = server_difference_dict.keys()
                summed_diffs = []
                for key in server_difference_keys:
                    summed_diff = 0
                    used_xs = set()
                    for diff_tuple in server_difference_dict[key]:
                        diff = diff_tuple[0]
                        x = diff_tuple[1]
                        server = diff_tuple[2]
                        if x not in used_xs:
                            used_xs.add(x)
                            summed_diff = summed_diff + diff
                    summed_diffs.append((summed_diff % util.get_prime(), server, key))
                equality = True
                first_element = summed_diffs[0]
                for element in summed_diffs[1:]:
                    if not np.array_equal(np.array(element[0]), np.array(first_element[0])):
                        equality = False
                        diffs = (element, first_element)
                        server = (element[1], first_element[1])
                        key = element[1]
                        server_util.complain_consistency(
                            util.Complaint(my_name, dict(
                                diffs=util.vote_to_string(diffs[3]),
                                key = key
                            ), util.Protocol.sum_difference_zero_one), server_util.list_remove(util.servers,
                                                        [my_name, util.servers[x]]),
                            util.mediator, my_name
                        )
                if not equality:
                    # TODO: DO SOMETHING HERE
                    print("sumdifferenceshareforzeroone: ", "Disagreement. Some differences are not equal!")
                    # disagreed_clients.append((client, i, j, difference_matrix_list[i][j][x][1], difference_matrix_list[i][j][x][2]))
        sum_product_zero_one_check()
        return Response(status=200)


def sum_product_zero_one_check():
    global communication_number
    zero_partitions_dict = db.get_zero_partitions(my_name)
    zero_partitions_clients = zero_partitions_dict.keys()
    for c in zero_partitions_clients:
        sum_partition_array = [[[0 for x in range(len(servers))] for j in range(len(servers))] for i in range(len(servers))]
        client_parts = zero_partitions_dict[c]
        used_parts = set()
        for part in client_parts:
            matrix = part['matrix']
            i = part['i']
            j = part['j']
            x = part['x']
            if (i, j, x) not in used_parts:
                used_parts.add((i, j, x))
                sum_partition_array[i][j][x] = np.mod(np.add(sum_partition_array[i][j][x], matrix),util.get_prime())
        communication_number += 3
        server_util.broadcast(data=dict(sum_matrix=util.vote_to_string(sum_partition_array), server=my_name, client=c), servers=servers, url="/zeroone_sum_partition")
        db.insert_zero_partition_sum(matrix=sum_partition_array, server=my_name, client=c, db_name=my_name)


@app.route("/zeroone_sum_partition", methods=["POST"])
def sum_product_receive():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    try:
        sum_matrix_ = data['sum_matrix']
        sum_matrix_ = util.string_to_vote(sum_matrix_)
        client_ = data['client']
        server_ = data['server']

        # Save on database
        db.insert_zero_partition_sum(matrix=sum_matrix_, client=client_, server=server_, db_name=my_name)
    except TypeError as e:
        print("zeroone_sum_partition: ", "ERROR")

    return Response(status=200)


def zeroone_sum_partition_finalize(): # check for vote validity
    partition_sums = db.get_zero_partition_sum(my_name)
    partition_sums_clients = partition_sums.keys()
    illegal_votes = []
    for client in partition_sums_clients:
        is_breaking = False
        part_sums = list(partition_sums[client])

        res = [[[[0] for x in range(len(servers))] for j in range(len(servers))] for i in range(len(servers))]
        res2 = [[[0] for j in range(len(servers))] for i in range(len(servers))]
        for i in range(len(servers)):
            for j in range(len(servers)):
                for x in range(len(servers)):
                    val = part_sums[0]['matrix'][i][j][x]
                    for part_sum in part_sums[1:]:
                        part_sum_matrix = part_sum['matrix']
                        if not np.array_equal(part_sum_matrix[i][j][x], np.zeros(part_sum_matrix[i][j][x].shape)):
                            if not np.array_equal(val, part_sum_matrix[i][j][x]):
                                # TODO: Disagreement
                                server_util.complain_consistency(
                                    util.Complaint(my_name, dict(),
                                                   util.Protocol.zero_one_finalize, x),
                                    server_util.list_remove(util.servers,
                                                            [my_name, util.servers[x]]),
                                    util.mediator, my_name
                                )
                                print("zeroone_sum_partition_finalize: ", "Disagreement! MEDIATOR not implemented yet")
                                is_breaking = True
                                break

                                print("zeroone_sum_partition_finalize: ", "Disagreement! MEDIATOR not implemented yet", client)
                            server = part_sum['server']
                        res[i][j][x] = val[0]
                    if is_breaking:
                        break
                if is_breaking:
                    break
                res2[i][j] = sum(res[i][j])[0] % util.get_prime()

            if is_breaking:
                break
        if is_breaking:
            continue
        sum_res = [sum(ij) for ij in res2]
        sum_res = np.mod(np.array(sum_res), util.get_prime())
        if not np.mod(np.sum(sum_res),util.get_prime()) == 0.0:
            # Illegal vote.
            illegal_votes.append(client)
    return illegal_votes


@app.route("/ensure_vote_agreement", methods=["GET"])
def ensure_agreement():
    global communication_number
    illegal_votes = []

    illegal = db.get_illegal_votes(my_name)
    sender_client_dict = defaultdict(list)
    for sender, client in illegal:
        sender_client_dict[sender].append(client)

    illegal_votes.append([x[1] for x in db.get_illegal_votes(my_name)])

    to_be_deleted = set()

    # TODO: Brug verify_consistency til at verificere alting
    print("ensure_vote_agreement: senders:", str(sender_client_dict.keys()))
    print("ensure_vote_agreement: values:", str(sender_client_dict.values()))
    agreed_illegal_votes = set(sender_client_dict[my_name][0])
    disagreed_illegal_votes = set()
    for server in servers:
        agreed_illegal_votes = agreed_illegal_votes.intersection(sender_client_dict[server][0])
        disagreed_illegal_votes = disagreed_illegal_votes.union(sender_client_dict[server][0])
    disagreed_illegal_votes = disagreed_illegal_votes.difference(agreed_illegal_votes)
    to_be_deleted = to_be_deleted.union(agreed_illegal_votes)

    for client in to_be_deleted:
        db.remove_vote(client, my_name)

    if(len(disagreed_illegal_votes) > 0):
        communication_number += 1
        server_util.complain_consistency(
            util.Complaint(my_name, dict(disagreed = disagreed_illegal_votes),
                           util.Protocol.ensure_vote_agreement, -1),
            server_util.list_remove(util.servers, my_name), util.mediator, my_name
        )

    return Response(status=200)


@app.route("/mediator_answer_votes", methods=["POST"])
def mediator_answer_votes():
    global malicious_server, found_malicious_server
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    # TODO: Check at mediator ikke er adversary
    malicious_server_ = data['malicious_server']
    if(malicious_server_ == ""):
        votes_for_deletion_ = data['votes_for_deletion']
        for client in votes_for_deletion_:
            db.remove_vote(client, my_name)
    else:
        found_malicious_server = True
        malicious_server = malicious_server_
        if (my_name != malicious_server_):
            for sender, votes in db.get_illegal_votes(my_name):
                if(sender == my_name):
                    for client in votes:
                        db.remove_vote(client, my_name)
    return Response(status=200)


@app.route("/messageinconsistency", methods=["POST"])
def messageinconsistency():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)

    # Modtager complaints fra andre servere
    # TODO: send relevant data to mediator
    return make_response("delivered", 200)


@app.route("/add", methods=["GET"])
def add():
    global communication_number
    votes = db.round_one(my_name)
    legal_votes = [x for x in votes if x[4] != malicious_server]

    # ss_summed_votes = server_util.secret_share(summed_votes, servers)

    summed_votes = server_util.sum_votes(legal_votes)
    communication_number += 3
    server_util.broadcast_values(summed_votes, 2, servers, my_name)
    return Response(status=200)


@app.route("/summed_votes", methods=["POST"])
def summed_votes():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    try:
        vote_ = data['vote']
        if type(vote_) == str:
            vote_ = [vote_]
        id_ = data['id']
        if type(id_) in [str, int]:
            id_ = [id_]
        client = data['client']
        server_name = data['server']

        for i in range(len(vote_)):
            vote = util.string_to_vote(vote_[i])
            assert type(vote) == np.ndarray
            db.insert_summed_votes(vote, int(id_[i]), client, server_name, my_name)
    except TypeError as e:
        print("summed_votes: ", vote_)
        print("summed_votes: ", e)
        return Response(status=400)

    return Response(status=200)


@app.route("/compute_result", methods=["GET"])
def compute_result():
    all_votes = db.round_two(my_name)
    legal_votes = [x for x in all_votes if x[3] != malicious_server]
    s = server_util.calculate_result(legal_votes)
    if cheat_id == 5:
        print ("compute_result: cheating")
        s = cheat_util.col_row_cheat(s)

    # Calculate Dowdall result.
    dowdall_result = np.array([sum([s[i][j]*(1/(j + 1))  for j in range(s.shape[0])]) for i in range(s.shape[1])])

    server_util.broadcast(dict(
        server=my_name,
        result=util.vote_to_string(dowdall_result),
        sender=my_name
    ), util.servers, "/save_result")
    return make_response("ok", 200)  # Response(util.vote_to_string(s), status=200, mimetype='text/text')


@app.route("/save_result", methods=["POST"])
def save_result():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    try:
        result_ = data['result']
        server_name = data['server']
        
        result = util.string_to_vote(result_)
        assert type(result) == np.ndarray
        db.insert_result(result, server_name, my_name)
    except TypeError as e:
        print("save_result: ", result_)
        print("save_result: ", e)
        return Response(status=400)

    return Response(status=200)


@app.route("/verify_result", methods=["GET"])
def verify_result():
    res_count = db.get_results_count(my_name)
    if res_count == 1:
        return make_response(util.vote_to_string(db.get_results(db_name=my_name)[0][0]), 200)
    results = db.get_results(my_name)
    results_to_verify = [(x[0], 0, x[1]) for x in results]
    _, v1, v2 = server_util.verify_consistency(results_to_verify)
    server_util.complain_consistency(
        util.Complaint(my_name,
                       dict(votes=[v1, v2]),
                       util.Protocol.compute_result,
                       -1),
        server_util.list_remove(util.servers, my_name), util.mediator, my_name)

    return make_response("Error, multiple results", 400)


@app.route("/get_comms", methods=["GET"])
def get_comms():
    global communication_number
    return make_response(str(communication_number), 200)

@app.route("/illegal", methods=["POST"])
def illegal_vote():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    bad_votes = data['clients']
    server_name = data['server']
    # print("illegal: ", "Got votes", bad_votes, "from server", server_name)
    db.insert_illegal_votes(bad_votes, server_name, my_name)
    return Response(status=200)

@app.route("/malicious", methods=["GET"])
def malicious():
    global malicious_server, found_malicious_server
    if not found_malicious_server:
        return make_response("", 200)
    else:
        return make_response(malicious_server, 200)


def create_local(port, cheat=False, cheating_ns=[], cheatid=0):
    global my_name, testing, server_nr, cheating, cheating_nums, cheat_id
    cheating = cheat
    cheating_nums = cheating_ns
    cheat_id = cheatid

    @app.route("/shutdown")
    def stop_server():
        print("stopping", port)
        shutdown_server()
        return 'Server shutting down...'

    util.get_keys(str(port))

    testing = True
    my_name = "http://127.0.0.1:" + str(port)
    server_nr = int(port)
    communication_number = 0
    print("starting ", port)
    app.run(port=int(port), debug=False, use_reloader=False, threaded=True)


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    port = sys.argv[1]
    create_local(port)
