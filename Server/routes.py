#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request, Response
from Server import database as db
import os
from Server import server_util
import util
import sys
import pickle
import numpy as np
import codecs


app = Flask(__name__)
app.url_map.strict_slashes = False

# numbers = defaultdict(list)
testing = False  # variabel til at slå database fra hvis vi kører det lokalt

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
    "http://127.0.0.1:5002"
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



@app.route("/")
def home():
    return server_util.home(db, my_name)

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


@app.route("/vote", methods=["POST"])
def receive_vote():
    try:
        vote_ = request.form['vote']
        vote = pickle.loads(codecs.decode(vote_.encode(), "base64"))
        assert type(vote) == np.ndarray
        id = request.form['id']
        round = request.form['round']
        client = request.form['client']
        print("RECEIVED VOTE IS: ", vote, " IN ROUND ", round, " FROM CLIENT ", client, " WITH ID: ", id)
        server_name = request.form['server']
        db.insert_vote(vote, id, round, client, server_name, my_name)
    except TypeError as e:
        print(vote_)
        print(e)
        return Response(status=400)

    # print("Values inserted")
    return Response(status=200)


@app.route("/add", methods=["GET"])
def add():
    votes = db.round_one(my_name)
    print("server: ", my_name)
    summed_votes = server_util.sum_votes(votes, servers, my_name)
    # TODO: Secret share summed votes
    server_util.broadcast_values(summed_votes, servers, my_name)
    return Response(status=200)


@app.route("/compute_result", methods=["GET"])
def compute_result():
    #TODO: check that all received values from round two match each other and make
    all_votes = db.round_two(my_name)
    server_nr = servers.index(my_name)
    s = server_util.calculate_s(all_votes, servers)
    return Response(status=200)


@app.route("/multiply", methods=["GET"])
def multiply():
    all_values = db.round_one(my_name)
    multiplication_values = [x for x in all_values if x[1] == 'm']
    print(str(multiplication_values))
    res = server_util.multiply(multiplication_values, servers, my_name)
    return Response(status=200)


def create_local(port):
    global my_name, testing, server_nr
    @app.route("/shutdown")
    def stop_server():
        shutdown_server()
        return 'Server shutting down...'

    testing = True
    my_name = "http://127.0.0.1:" + str(port)
    server_nr = int(port) - 5000
    app.run(port=int(port), debug=True, use_reloader=False)


@app.route("/server", methods=["POST"])
def server():
    values = request.form.getlist("value")
    clients = request.form.getlist("client")
    servers = request.form.getlist("server")
    name = request.form.getlist("name")
    id = request.form.getlist("id")
    for num, n in enumerate(name):
        db.insert_number(int(values[num]) % util.get_prime(), n, id[num], clients[num], servers[num], my_name)
    return Response(status=200)

if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    port = sys.argv[1]
    create_local(port)
