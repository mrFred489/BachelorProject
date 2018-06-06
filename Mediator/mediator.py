from flask import Flask, request, Response, make_response
import logging
import util
from Server import database as db


app = Flask(__name__)
app.url_map.strict_slashes = False
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

my_name = "mediator"

test_servers = [
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003",
]

servers = test_servers


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
    illegal_votes_ = data['illegal_votes']
    if type(illegal_votes_) == str:
        illegal_votes_ = [illegal_votes_]
    server_ = data['server']
    db.insert_mediator_illegal_votes(illegal_votes_, server_)
    return make_response("valid", 200)


@app.route("/decidevalidity", methods=["POST"])
def decide_validity():
    sender_illegal_votes = db.get_mediator_illegal_votes()

    full_illegal_set = set()
    sender_dict = dict()
    for sender, clients in sender_illegal_votes:
        full_illegal_set = full_illegal_set.union(set(clients))
        sender_dict[sender] = clients

    malicious_server = ""
    votes_to_be_deleted = set()
    for vote in full_illegal_set:
        complaining_servers = set()
        for sender in sender_dict.keys():
            if vote in sender_dict[sender]:
                complaining_servers.add(sender)
        complaints = len(complaining_servers)

        if complaints == 1:
            # complaining server is malicious
            malicious_server = complaining_servers[0]

        if complaints == 2:
            # If this happens something horrible has gone wrong. Shouldn't be possible scenario in correct setup
            return make_response("Two complaints. Mediator is confused", 400)

        if complaints == 3:
            # noncomplaining server is malicious
            malicious_server = set(sender_dict.keys()).difference(complaining_servers)[0]
            votes_to_be_deleted.add(vote)

        if complaints == 4:
            # vote should be deleted. Should not happen
            votes_to_be_deleted.add(vote)

    if malicious_server == "":
        broadcast_to_servers(dict(malicious_server=malicious_server, votes_for_deletion=votes_to_be_deleted), url="/mediator_answer_votes")
    else:
        broadcast_to_servers(dict(malicious_server=malicious_server, votes_for_deletion=[]), url="/mediator_answer_votes")


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


def broadcast_to_servers(data:  dict, url: str):
    for server in servers:
        util.post_url(data=data, url=url)
