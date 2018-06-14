from flask import Flask, request, make_response
import logging
import util
from Server import database as db
import multiprocessing as mp
import time
import threading
from Server import server_util
import numpy as np


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

def timer(t, protocol, complaint):
    util.get_keys("mediator")
    pr = mp.Process(target=handle_complaint, args=(t, protocol,complaint))
    pr.start()


locks = [False for _ in range(6)]

semaphore = threading.Semaphore()


def answer_complaint(complaint, malicious_server, votes_for_deletion):
    for server in util.servers:
        util.post_url(dict(
            complaint=util.vote_to_string(complaint),
            malicious_server=malicious_server,
            sender=my_name,
            votes_for_deletion=votes_for_deletion
        ),server + "/mediator_answer_votes")


def use_majority(relevant, complaint):
    if len(relevant) > 1:
        temp = server_util.list_remove(util.servers, util.servers[complaint.value_id])
        for i in set(relevant + [util.servers[complaint.value_id], complaint.sender]):
            temp = server_util.list_remove(util.servers, i)
        if temp != []:
            malicious_server = temp[0]
    else:
        malicious_server = complaint.sender
    return malicious_server


        
def handle_complaint(t, protocol, complaint):
    time.sleep(t)
    semaphore.acquire()
    if locks[protocol.value-1]:
        semaphore.release()
        return
    locks[protocol.value-1] = True
    semaphore.release
    # extra_data = db.get_mediator_inconsistency_extra_data_for_protocol(protocol)
    other_complaints = [x for x in db.get_mediator_inconsistency() if x[2] == protocol]
    malicious_server = ""
    votes_for_deletion = ""
    if complaint.protocol == util.Protocol.check_votes:
        votes = complaint.data["votes"]
        relevant = [x[1] for x in other_complaints
                    if (x[0] != complaint.sender
                        and server_util.nparray_in_list(x[1].data["votes"][0], votes)
                        and server_util.nparray_in_list(x[1].data["votes"][1], votes))]
        malicious_server = use_majority(relevant, complaint)
    elif complaint.protocol == util.Protocol.sum_difference_zero_one:
        diffs = complaint.data["diffs"]
        relevant = [x[1] for x in other_complaints
                    if (x[0] != complaint.sender
                        and server_util.list_of_nparray_in_list(x[1].data["diffs"], diffs)
                        and complaint.data["i"] == x[1].data["i"]
                        and complaint.data["j"] == x[1].data["j"]
                        and complaint.data["key"] == x[1].data["key"]
                        and complaint.data["client"] == x[1].data["client"])]
        malicious_server = use_majority(relevant, complaint)
    elif complaint.protocol == util.Protocol.sum_difference_zero_one_partition:
        relevant = [x[1] for x in other_complaints
                    if (x[0] != complaint.sender
                        and complaint.data["i"] == x[1].data["i"]
                        and complaint.data["j"] == x[1].data["j"]
                        and complaint.data["x"] == x[1].data["x"]
                        and complaint.data["diff2"] == x[1].data["diff2"]
                        and complaint.data["diff1"] == x[1].data["diff1"]
                        and complaint.data["key"] == x[1].data["key"]
                        and complaint.data["client"] == x[1].data["client"])]
        malicious_server = use_majority(relevant, complaint)
    elif complaint.protocol == util.Protocol.zero_one_finalize:
        print("type of part_sum:", type(complaint.data["part_sum"]))
        relevant = [x[1] for x in other_complaints
                    if (x[0] != complaint.sender
                        and complaint.data["i"] == x[1].data["i"]
                        and complaint.data["j"] == x[1].data["j"]
                        and complaint.data["x"] == x[1].data["x"]
                        and np.array_equal(complaint.data["part_sum"], x[1].data["part_sum"])
                        and np.array_equal(complaint.data["val_matrix"], x[1].data["val_matrix"])
                        and complaint.data["key"] == x[1].data["key"]
                        and complaint.data["client"] == x[1].data["client"])]
        malicious_server = use_majority(relevant, complaint)
    elif complaint.protocol == util.Protocol.ensure_vote_agreement:
        majority_senders = set()
        majority_senders.add(complaint.sender)
        for c in other_complaints:
            if c[0] in list(majority_senders):
                continue
            if complaint.data["disagreed_illegal_votes"] == c[1].data["disagreed_illegal_votes"]:
                majority_senders.add(c[0])
        malicious_server = use_majority(list(majority_senders), complaint)
    elif complaint.protocol == util.Protocol.compute_result:
        majority_senders = set()
        majority_senders.add(complaint.sender)
        for c in other_complaints:
            if c[0] in majority_senders:
                continue
            if np.array_equal(complaint.data["results"], c[1].data["results"]):
                majority_senders.add(c[0])
        malicious_server = use_majority(list(majority_senders), complaint)

    answer_complaint(complaint, malicious_server, votes_for_deletion)
    locks[protocol.value-1] = False


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
            # Ask for relevant values from all servers who has them, and compute correct value. 
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


    # check_votes = 1
    # sum_difference_zero_one = 2
    # sum_difference_zero_one_partition = 3
    # zero_one_finalize = 4
    # ensure_vote_agreement = 5
    # compute_result = 6


@app.route("/extra_data", methods=["POST"])
def extra_data():
    verified, data = util.unpack_request(request, my_name)
    if not verified:
        return make_response("Could not verify", 400)
    complaint = util.string_to_vote(data["complaint"])
    db.insert_mediator_inconsistency_extra_data(data["sender"], complaint, complaint.protocol, data["data"])
    return make_response("ok", 200)

    

@app.route("/messageinconsistency", methods=["POST"])
def message_inconsistency():
    verified, data = util.unpack_request(request, my_name)
    if not verified:
        return make_response("Could not verify", 400)
    complaint: util.Complaint = util.string_to_vote(data["complaint"])
    
    db.insert_mediator_inconsistency(complaint.sender, complaint, complaint.protocol)
    timer(5, complaint.protocol, complaint)
    return make_response("Done", 200)


@app.route("/reset", methods=["POST"])
def reset():
    db.reset_mediator()
    return make_response("ok", 200)


@app.route("/test/printcomplaints", methods=["GET"])
def test_printComplaints():
    # print(db.get_mediator_inconsistency())
    return make_response(str(db.get_mediator_inconsistency()), 200)


def create_local(port):
    global my_name, testing
    @app.route("/shutdown")
    def stop_server():
        shutdown_server()
        return 'Server shutting down...'

    util.get_keys(my_name)

    testing = True
    app.run(port=int(port), debug=False, use_reloader=False, threaded=True)


def broadcast_to_servers(data: dict, url: str):
    for server in servers:
        util.post_url(data=data, url=url)
