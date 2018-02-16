#!/usr/bin/env python3
from functools import wraps
import werkzeug.contrib
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.url_map.strict_slashes = False

numbers = [defaultdict(set) for i in range(3)]

round2 = defaultdict(list)


@app.route("/")
def home():
    return str(numbers)

@app.route("/server<int:id>", methods=["POST"])
def server(id):
    name = request.form.get("name")
    value = request.form.get("value")
    numbers[id][name].add((id, value))
    print(request.method)
    print(request.json)
    
    for i in request.json:
        print(i, request.json.get(i))
        
    return render_template("server.html", name=str(id), sum=value)
                                            

if __name__ == '__main__':
    # app.run(port=80)
    app.run(debug=True)

    
