#!/usr/bin/env python3
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response

app = Flask(__name__)
app.url_map.strict_slashes = False

numbers = defaultdict(list)
p = 4000001
testing = False # variabel til at slå database fra hvis vi kører det lokalt

@app.route("/")
def home():
    servers = []
    total = 0
    for index in numbers:
        servers.append({"num": index, "data": str(numbers[index])})
        total += sum(numbers[index])
    return render_template("server.html", servers=servers, total=total % p)

@app.route("/total")
def total():
    total = 0
    for i in range(5):
        total += sum(numbers[i])
    return str(total % p)

@app.route("/reset", methods=["POST"])
def reset():
    for i in numbers:
        numbers[i] = []
    return Response(status=200)


@app.route("/databases")
def database():
    return str(numbers)


@app.route("/server<int:id>", methods=["POST"])
def server(id):
    name = request.form.get("name")
    value = request.form.get("value")
    numbers[id].append(int(value) % p)
    return Response(status=200)


@app.route("/server<int:id>/prime", methods=['GET'])
def prime(id):
    return str(p)


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    testing = True
    port = input('Choose port for server: ')
    app.run(port=int(port), debug=True, use_reloader=False)


