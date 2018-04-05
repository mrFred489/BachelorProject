#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request, Response, make_response
from Server import database as db
import os
from Server import server_util
import util
import sys
import numpy as np
from time import sleep
import logging
from collections import defaultdict
import math


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
    "http://127.0.0.1:5003",
    "http://127.0.0.1:5004",
]

official_servers = [
    "https://cryptovoting.dk/",
    "https://server1.cryptovoting.dk/",
    "https://server2.cryptovoting.dk/",
    "https://server3.cryptovoting.dk/",
    # "https://server4.cryptovoting.dk/"
    ]

if not testing:
    servers = test_servers
else:
    servers = official_servers


@app.route("/total")
def total_sum():
    totals = []
    names = set()
    numbers = db.round_one(my_name)
    for i in numbers:
        if i[2] not in names:
            totals.append(("s" + str(i[2]), sum([x[0] if x[2] == i[2] else 0 for x in numbers]) % util.get_prime()))
            names.add(i[2])
    return str(totals)


@app.route("/reset", methods=["POST"])
def reset():
    db.reset(my_name)
    return Response(status=200)


@app.route("/databases")
def database():
    return str(db.round_one(my_name))


@app.route("/submit", methods=["POST"])
def receive_vote():
    try:
        vote_ = request.form.getlist('vote')
        id_ = request.form.getlist('id')
        round_ = request.form['round']
        client = request.form['client']
        server_name = request.form['server']

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
            servers_copy = servers.copy()
            servers_copy.remove(my_name)
            for server_name in servers_copy:
                util.post_url(data=dict(client=client, server=my_name, vote=util.vote_to_string(check)),
                              url=server_name + "/zerocheck")
    except TypeError as e:
        print(vote_)
        print(e)
        return Response(status=400)

    return Response(status=200)


@app.route("/server_comm", methods=["POST"])
def receive_broadcasted_value():
    vote_ = request.form['vote']
    vote = util.string_to_vote(vote_)
    assert type(vote) == np.ndarray
    id_ = request.form['id']
    type_ = request.form['round']
    client = request.form['client']
    server_name = request.form['server']
    if type_ == 'row':
        db.insert_row(vote, id_, type_, client, server_name, my_name)
    elif type_ == 'column':
        db.insert_col(vote, id_, type_, client, server_name, my_name)
    return Response(status=200)


@app.route("/add", methods=["GET"])
def add():
    votes = db.round_one(my_name)
    summed_votes = server_util.sum_votes(votes)
    # TODO: Secret share summed votes
    # ss_summed_votes = server_util.secret_share(summed_votes, servers)
    server_util.broadcast_values(summed_votes, 2, servers, my_name)
    return Response(status=200)

@app.route("/check_votes", methods=["GET"])
def check_votes():

    # ZERO ONE CHECK
    zerocheck_values = db.get_zero_check(my_name)  # [(matrix, client, server), ...]
    illegal_votes = server_util.zero_one_illegal_check(zerocheck_values)

    # COLUMN ROW CHECK
    cols = db.get_cols(my_name)
    rows = db.get_rows(my_name)
    illegal_votes.union(server_util.verify_sums(rows))
    illegal_votes.union(server_util.verify_sums(cols))

    # ?
    all_votes = db.round_two(my_name)
    if not server_util.verify_consistency(all_votes):
        return Response(status=400)


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

    agreed_illegal_votes = set()
    disagreed_illegal_votes = set()
    for i in range(len(servers)):
        agreed_illegal_votes.intersection(illegal_votes[i])
        disagreed_illegal_votes.union(illegal_votes[i])
    disagreed_illegal_votes.difference(agreed_illegal_votes)
    to_be_deleted.union(agreed_illegal_votes)

    # Check for majority disagreement
    majority_legal = set()
    majority_illegal = set()
    for client in disagreed_illegal_votes:
        observations = 0
        for il_clients in illegal_votes:
            if client in il_clients:
                observations =+ 1
        if(observations>math.floor(len(servers)/2)):
            majority_legal.add(client)
        else: majority_illegal.add(client)
    to_be_deleted.union(majority_illegal)

    # Delete illegal and majority illegal votes
    for client in to_be_deleted:
        db.remove_vote(client, my_name)

    # Agree on majority legal votes
        # TODO: Find out which servers have the correct secret shares for each non-conclusive legal vote, so that these
        # servers are the only ones to calculate these votes
    return Response(status=200)


@app.route("/compute_result", methods=["GET"])
def compute_result():
    # TODO: rewrite calculate result. Illegal_votes need to removed sooner
    illegal_votes = []
    all_votes = db.round_two(my_name)
    # print("av", all_votes)
    s = server_util.calculate_result(all_votes, illegal_votes)
    return make_response(util.vote_to_string(s))  # Response(util.vote_to_string(s), status=200, mimetype='text/text')

@app.route("/zerocheck", methods=["POST"])
def zerocheck():
    try:
        vote_ = request.form['vote']
        vote = util.string_to_vote(vote_)
        assert type(vote) == np.ndarray
        client = request.form['client']
        server_name = request.form['server']
        db.insert_zero_check(vote, client, server_name, my_name)

    except TypeError as e:
        print(vote_)
        print(e)
        return Response(status=400)

    return Response(status=200)

@app.route("/illegal", methods=["POST"])
def illegal_vote():
    bad_votes = request.form.getlist('clients')
    server_name = request.form['server']
    db.insert_illegal_votes(bad_votes, server_name, my_name)
    return Response(status=200)


@app.route("/multiply", methods=["GET"])
def multiply():
    pass


def create_local(port):
    global my_name, testing, server_nr
    @app.route("/shutdown")
    def stop_server():
        shutdown_server()
        return 'Server shutting down...'

    testing = True
    my_name = "http://127.0.0.1:" + str(port)
    server_nr = int(port) - 5000
    app.run(port=int(port), debug=False, use_reloader=False, threaded=True)


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    port = sys.argv[1]
    create_local(port)
