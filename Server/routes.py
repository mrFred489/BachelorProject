#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request, Response
from Server import database as db
import os
from Server import server_util
import util
import sys


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
    numbers = db.get_numbers(my_name)
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
    return str(db.get_numbers(my_name))


@app.route("/vote", methods=["POST"])
def receive_vote():
    r_i = request.form['val']
    i = request.form['index']
    col = request.form['col']
    row = request.form['row']
    client = request.form['client']
    server_name = request.form['server']
    db.insert_r_i(r_i, i, col, row, client, server_name, my_name)
    print("Values inserted")
    return Response(status=200)


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



@app.route("/add", methods=["GET"])
def add():
    votes = db.get_numbers(my_name)
    server_nr = servers.index(my_name)

    s_array = server_util.sum_r_values(votes, servers, server_nr)

    for num, value in enumerate(s_array):
        if num != server_nr:
            # my_name my_name my_name
            db.insert_number(value, 's', num , my_name, my_name, my_name)
    server_util.broadcast_values(s_array, servers, my_name)

    # return value is never used
    return jsonify({'s': s_array})


@app.route("/compute_result", methods=["GET"])
def compute_result():
    all_votes = db.get_numbers(my_name)
    server_nr = servers.index(my_name)
    s = server_util.calculate_s(all_votes, servers)
    return jsonify({'s': s})


@app.route("/multiply", methods=["GET"])
def multiply():
    all_values = db.get_numbers(my_name)
    multiplication_values = [x for x in all_values if x[1] == 'm']
    print(str(multiplication_values))
    res = server_util.multiply(multiplication_values, servers, my_name)
    return jsonify({'res': res})


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


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    port = sys.argv[1]
    create_local(port)
