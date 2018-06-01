#!/usr/bin/env python3
from flask import Flask, request, Response, make_response
from Server import database as db
from Server import server_util
import util
import sys
import numpy as np
import logging
import math
import os.path

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

if not testing:
    servers = test_servers
    mediator = test_mediator
else:
    servers = official_servers

found_malicious_server = False
malicious_server = ""

@app.route("/reset", methods=["POST"])
def reset():
    db.reset(my_name)
    return Response(status=200)

@app.route("/vote", methods=["POST"])
def vote():
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
        for v_ in votes_:
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

        zero_one_check = server_util.matrix_zero_one_check(my_id, len(servers), votes_dict)
        db.insert_zero_check(zero_one_check, client, my_name, my_name)
        servers_copy = server_util.list_remove(servers, my_name)
        server_util.broadcast(dict(client=client, server=my_name, vote=util.vote_to_string(zero_one_check)), servers_copy,
                                  "/zerocheck")
    except TypeError as e:
        print(e)
        return Response(status=400)
    return Response(status=200)

@app.route("/submit", methods=["POST"])
def receive_vote():
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
        round_ = data['round']
        if type(round_) == str:
            round_ = [round_]
        client = data['client']
        server_name = data['server']
        # print("vote_", client, round_, server_name, id, "start vote", vote_, "slut vote")


        my_id = servers.index(my_name)

        votes = dict()
        for i in range(len(vote_)):
            vote = util.string_to_vote(vote_[i])
            assert type(vote) == np.ndarray
            votes[int(id_[i])] = vote
            db.insert_vote(vote, int(id_[i]), round_, client, server_name, my_name)
            if int(round_) == 1:
                row_sum = server_util.create_sum_of_row(vote)
                col_sum = server_util.create_sum_of_row(vote.T)

                db.insert_row(row_sum, id_[i], 'row', client, server_name, my_name)
                db.insert_col(col_sum, id_[i], 'column', client, server_name, my_name)

                server_util.broadcast_rows_and_cols(row_sum, col_sum, id_[i], servers, my_name, client)

            # x * ( x - 1)
        if int(round_) == 1:
            check = server_util.matrix_zero_one_check(my_id, len(servers), votes)
            db.insert_zero_check(check, client, my_name, my_name)
            servers_copy = server_util.list_remove(servers, my_name)
            server_util.broadcast(dict(client=client, server=my_name, vote=util.vote_to_string(check)), servers_copy,
                                  "/zerocheck")
    except TypeError as e:
        print(vote_)
        print(e)
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
        print(vote_)
        print(e)
        return Response(status=400)

    return Response(status=200)


@app.route("/check_votes", methods=["GET"])
def check_votes():
    # ZERO ONE CHECK
    zerocheck_values = db.get_zero_check(my_name)  # [(matrix, client, server), ...]
    illegal_votes = server_util.zero_one_illegal_check(zerocheck_values)

    # COLUMN ROW CHECK
    cols = db.get_cols(my_name)
    rows = db.get_rows(my_name)
    illegal_votes = illegal_votes.union(server_util.verify_sums(rows))
    illegal_votes = illegal_votes.union(server_util.verify_sums(cols))

    # TODO: Ensure agreement among servers regarding illegal_votes

    list_illegal_votes = list(illegal_votes)
    # Save own illegal votes
    db.insert_illegal_votes(list_illegal_votes, my_name, my_name)
    # Broadcast own illegal votes to others
    server_util.broadcast_illegal_votes(list_illegal_votes, my_name, servers)
    return Response(status=200)


@app.route("/ensure_vote_agreement", methods=["GET"])
def ensure_agreement():
    illegal_votes = []

    for server in servers:
        illegal_votes.append(db.get_illegal_votes(server)[1][1])

    to_be_deleted = set()


    agreed_illegal_votes = set(illegal_votes[0])
    disagreed_illegal_votes = set()
    for i in range(len(servers)):
        agreed_illegal_votes = agreed_illegal_votes.intersection(illegal_votes[i])
        disagreed_illegal_votes = disagreed_illegal_votes.union(illegal_votes[i])
    disagreed_illegal_votes = disagreed_illegal_votes.difference(agreed_illegal_votes)
    to_be_deleted = to_be_deleted.union(agreed_illegal_votes)

    for client in to_be_deleted:
        print("removing vote", client)
        db.remove_vote(client, my_name)


    disagreed_illegal_votes = ["c3"]
    # Send disagreed illegal votes to mediator
    if(len(disagreed_illegal_votes) > 0):
        server_util.send_illegal_votes_to_mediator(illegal_votes=list(disagreed_illegal_votes), server=my_name, url=mediator)


    return Response(status=200)

@app.route("/mediator_answer_votes", methods=["POST"])
def mediator_answer_votes():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
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


@app.route("/add", methods=["GET"])
def add():
    votes = db.round_one(my_name)
    summed_votes = server_util.sum_votes(votes)
    # TODO: Secret share summed votes

    # TODO: EXLUDE CORRUPT SERVER FROM TAKING PART.
    # ss_summed_votes = server_util.secret_share(summed_votes, servers)
    server_util.broadcast_values(summed_votes, 2, servers, my_name)
    return Response(status=200)


@app.route("/compute_result", methods=["GET"])
def compute_result():

    # TODO: EXCLUDE CORRUPT SERVERS FROM TAKING PART IN THIS.
    # TODO:
    all_votes = db.round_two(my_name)
    # print("av", all_votes)
    s = server_util.calculate_result(all_votes)

    # Broadcast result to other servers. If disagreement, then send to mediator.

    return make_response(util.vote_to_string(s))  # Response(util.vote_to_string(s), status=200, mimetype='text/text')


@app.route("/illegal", methods=["POST"])
def illegal_vote():
    verified, data = util.unpack_request(request, str(server_nr))
    if not verified:
        return make_response("Could not verify", 400)
    bad_votes = data['clients']
    server_name = data['server']
    print("Got votes", bad_votes, "from server", server_name)
    db.insert_illegal_votes(bad_votes, server_name, my_name)
    return Response(status=200)


def create_local(port):
    global my_name, testing, server_nr

    @app.route("/shutdown")
    def stop_server():
        print("stopping", port)
        shutdown_server()
        return 'Server shutting down...'

    util.get_keys(str(port))

    testing = True
    my_name = "http://127.0.0.1:" + str(port)
    server_nr = int(port)
    print("starting ", port)
    app.run(port=int(port), debug=False, use_reloader=False, threaded=True)


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    port = sys.argv[1]
    create_local(port)
