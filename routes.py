#!/usr/bin/env python3
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.url_map.strict_slashes = False

numbers = defaultdict(list)

@app.route("/")
def home():
    servers = []
    total = 0
    for index in numbers:
        servers.append({"num": index, "data": str(numbers[index])})
        total += sum(numbers[index])
    return render_template("server.html", servers=servers, total=total)

@app.route("/total")
def total():
    total = 0
    for i in range(5):
        total += sum(numbers[i])
    return str(total)

@app.route("/databases")
def database():
    return str(numbers)


@app.route("/server<int:id>", methods=["POST"])
def server(id):
    name = request.form.get("name")
    value = request.form.get("value")
    numbers[id].append(int(value))
    return [200]


if __name__ == '__main__':
    # Lav flere servere ved at ændre port nummeret og køre routes igen.
    app.run(port=5000, debug=True)


