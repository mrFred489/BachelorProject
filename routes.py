#!/usr/bin/env python3
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
import database as db

app = Flask(__name__)
app.url_map.strict_slashes = False

# numbers = defaultdict(list)
p = 4000001
testing = False # variabel til at slå database fra hvis vi kører det lokalt

@app.route("/")
def home():
    servers = []
    total = 0
    numbers = db.get_numbers()

    servers.append({"num": 0, "data": str(numbers)})
    total += sum(numbers)
    return render_template("server.html", servers=servers, total=total % p)

@app.route("/total")
def total():
    total = 0
    numbers = db.get_numbers()
    total += sum(numbers)
    return str(total % p)

@app.route("/reset", methods=["POST"])
def reset():
    db.reset()
    return Response(status=200)


@app.route("/databases")
def database():
    return db.get_numbers()


@app.route("/server<int:id>", methods=["POST"])
def server(id):
    name = request.form.get("name")
    value = request.form.get("value")
    db.add_number(int(value) % p, name)
    return Response(status=200)


@app.route("/server<int:id>/prime", methods=['GET'])
def prime(id):
    return str(p)


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    testing = True
    port = input('Choose port for server: ')
    app.run(port=int(port), debug=True, use_reloader=False)


