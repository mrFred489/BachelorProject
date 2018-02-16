#!/usr/bin/env python3
from functools import wraps
import werkzeug.contrib
from collections import defaultdict
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.url_map.strict_slashes = False

numbers = defaultdict(list)
round2 = defaultdict(list)


@app.route("/")
def home():
    return string(numbers)

@app.route("/bp/server<int:name>", methods=["POST"])
def server(id):
    name1 = request.form.get("name")
    value1 = request.form.get("value")
    numbers[id].append((value1, name1))
    print(request.method)
    print(request.json)
    
    for i in request.json:
        print(i, request.json.get(i))
        
    return render_template("server.html", name=str(name), sum=value1)
                                            

if __name__ == '__main__':
    # app.run(port=80)
    app.run(debug=True)

    
