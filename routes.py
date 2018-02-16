#!/usr/bin/env python3
from functools import wraps
import werkzeug.contrib
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.url_map.strict_slashes = False

numbers = defaultdict(list)

@app.route("/")
def sum():
    sum = 0
    for i in range(5):
        for x in numbers[i]:
            sum += int(x)
    return str(sum)

@app.route("/databases")
def database():
    return str(numbers)


@app.route("/server<int:id>", methods=["POST"])
def server(id):
    name = request.form.get("name")
    value = request.form.get("value")
    numbers[id].append(value)
        
    return render_template("server.html", name=str(id), sum=value)
                                            

if __name__ == '__main__':
    # app.run(port=80)
    app.run(debug=True)

    
