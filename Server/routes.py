#!/usr/bin/env python3
from flask import Flask, render_template, request, Response
from Server import database as db
import os
from Server import server_util
import util
import sys
import requests


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


@app.route("/")
def home():
    return server_util.home(db, my_name)
    # servers = []
    # total = 0
    # numbers = db.get_numbers(my_name)
    # servers.append({"data": str(numbers)})
    # total += sum([x[0] for x in numbers])
    # return render_template("server.html", servers=servers, total=total % util.get_prime())


@app.route("/total")
def total_sum():
    totals = []
    names = set()
    numbers = db.get_numbers(my_name)
    for i in numbers:
        if i[1] not in names:
            totals.append((i[1].replace("r", "s"), sum([x[0] if x[1] == i[1] else 0 for x in numbers]) % util.get_prime()))
            names.add(i[1])
    return str(totals)


@app.route("/reset", methods=["POST"])
def reset():
    db.reset(my_name)
    return Response(status=200)


@app.route("/databases")
def database():
    return str(db.get_numbers(my_name))


@app.route("/server", methods=["POST"])
def server():
    values = request.form.getlist("value")
    clients = request.form.getlist("client")
    servers = request.form.getlist("server")
    for num, n in enumerate(request.form.getlist("name")):
        db.insert_number(int(values[num]) % util.get_prime(), n, clients[num], servers[num], my_name)
    return Response(status=200)


def create_local(port):
    global my_name, testing
    @app.route("/shutdown")
    def stop_server():
        shutdown_server()
        return 'Server shutting down...'

    testing = True
    my_name = "http://127.0.0.1:" + str(port)
    app.run(port=int(port), debug=True, use_reloader=False)


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    port = sys.argv[1]
    create_local(port)
