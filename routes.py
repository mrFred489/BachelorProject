#!/usr/bin/env python3
from functools import wraps
import werkzeug.contrib
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.url_map.strict_slashes = False

@app.route("/")
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    # app.run(port=80)
    app.run(debug=True)

    
