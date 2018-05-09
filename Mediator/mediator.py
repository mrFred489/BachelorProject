from flask import Flask, request, Response, make_response
import logging
import util
from Server import database as db


app = Flask(__name__)
app.url_map.strict_slashes = False
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

my_name = "mediator"

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route("/votevalidity", methods=["POST"])
def vote_validity():
    verified, data = util.unpack_request(request, my_name)
    if not verified:
        return make_response("Could not verify", 400)
    return make_response(200)


@app.route("/messageinconsistency", methods=["POST"])
def message_inconsistency():
    verified, data = util.unpack_request(request, my_name)
    if not verified:
        return make_response("Could not verify", 400)
    return make_response(200)


def create_local(port):
    global my_name, testing
    @app.route("/shutdown")
    def stop_server():
        shutdown_server()
        return 'Server shutting down...'

    util.get_keys(my_name)

    testing = True
    app.run(port=int(port), debug=False, use_reloader=False, threaded=True)
