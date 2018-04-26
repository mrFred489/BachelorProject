from flask import Flask, request, Response, make_response
import logging
import util


app = Flask(__name__)
app.url_map.strict_slashes = False
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route("/votevalidity", methods=["POST"])
def vote_validity():
    verified, data = util.unpack_request(request, str(server_nr))


@app.route("/messageinconsistency", methods=["POST"])
def message_inconsistency():
    verified, data = util.unpack_request(request, str(server_nr))


def create_local(port):
    global my_name, testing, server_nr
    @app.route("/shutdown")
    def stop_server():
        shutdown_server()
        return 'Server shutting down...'

    util.get_keys(str(port))

    testing = True
    my_name = "mediator"
    server_nr = int(port)
    app.run(port=int(port), debug=False, use_reloader=False, threaded=True)
