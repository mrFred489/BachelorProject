#!/usr/bin/env python3
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
import database as db
import os

app = Flask(__name__)
app.url_map.strict_slashes = False

# numbers = defaultdict(list)
p = 4000037
testing = False  # variabel til at slå database fra hvis vi kører det lokalt

try:
    my_name = str(os.path.dirname(__file__).split("/")[3])
except:
    my_name = "test"


@app.route("/")
def home():
    servers = []
    total = 0
    numbers = db.get_numbers(my_name)
    servers.append({"data": str(numbers)})
    total += sum([x[0] for x in numbers])
    return render_template("server.html", servers=servers, total=total % p)


@app.route("/total")
def total_sum():
    totals = []
    names = set()
    numbers = db.get_numbers(my_name)
    for i in numbers:
        if i[1] not in names:
            totals.append((i[1].replace("r", "s"), sum([x[0] if x[1] == i[1] else 0 for x in numbers]) % p))
            names.add(i[1])
    return str(totals)


@app.route("/reset", methods=["POST"])
def reset():
    db.reset(my_name)
    return Response(status=200)


@app.route("/databases")
def database():
    return db.get_numbers(my_name)


@app.route("/server", methods=["POST"])
def server():
    values = request.form.getlist("value")
    for num, n in enumerate(request.form.getlist("name")):
        db.insert_number(int(values[num]) % p, n, my_name)
    return Response(status=200)


@app.route("/server/prime", methods=['GET'])
def prime():
    return str(p)


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    testing = True
    port = input('Choose port for server: ')
    my_name = "http://127.0.0.1:" + str(port)
    app.run(port=int(port), debug=True, use_reloader=False)
