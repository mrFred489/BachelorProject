import util
import requests
import unittest
import time
from Client import client_util
import multiprocessing as mp
import Server.routes
from Server import server_util
import numpy as np
import os.path
import Mediator.mediator


baseurl1 = "http://127.0.0.1:5000"
baseurl2 = "http://127.0.0.1:5001"
baseurl3 = "http://127.0.0.1:5002"
baseurl4 = "http://127.0.0.1:5003"
mediator = "http://127.0.0.1:5100"

local_servers = [baseurl1, baseurl2, baseurl3, baseurl4]

local_servers_and_med = local_servers + [mediator]

official_server = "https://cryptovoting.dk"
official_server1 = "https://server1.cryptovoting.dk"
official_server2 = "https://server2.cryptovoting.dk"
official_server3 = "https://server3.cryptovoting.dk"
official_server4 = "https://server4.cryptovoting.dk"

n_servers = [baseurl1, baseurl2, baseurl3,
             official_server, official_server1,
             official_server2, official_server3, official_server4]

test_keys_necessary = ["", "c1", "c2", "mediator"] + [str(5000+i) for i in range(5)]

def create_local_server(port):
    pr = mp.Process(target=Server.routes.create_local, args=(str(port),))
    pr.start()

def create_local_cheating_server(port, cheating_nums, cheating_id):
    pr = mp.Process(target=Server.routes.create_local, args=(str(port), True, cheating_nums, cheating_id))
    pr.start()
    
def create_local_mediator(port):
    util.get_keys("mediator")
    pr = mp.Process(target=Mediator.mediator.create_local, args=(str(port),))
    pr.start()



class TestArithmetics(unittest.TestCase):

    def test_addition(self):
        secrets_1 = util.create_addition_secret(10, 2)
        secrets_2 = util.create_addition_secret(15, 2)
        res = (sum(secrets_1) + sum(secrets_2)) % util.get_prime()
        self.assertEqual(25, res)

    def test_signature(self):
        util.get_keys("")
        res = util.make_post_signature(dict(test="1234"))
        self.assertTrue(util.verify(bytes(res["signature"]), res["data"], res["pub"].decode()))

    def test_signature_neg(self):
        util.get_keys("")
        res = util.make_post_signature(dict(test="1234"))
        self.assertFalse(util.verify(bytes(res["signature"][:-1]), res["data"], res["pub"].decode()))




class TestCommunication(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for n in test_keys_necessary:
            if not os.path.isfile("cryp/public{}.pem".format(n)):
                util.get_keys(n)

        for i in range(4):
            create_local_server(5000 + i)

        create_local_mediator(5100)

        time.sleep(3)

    @classmethod
    def setUp(cls):
        reset_servers()
        time.sleep(0.1)

    def test_vote_format(self):
        vote = client_util.create_vote([4, 2, 1, 3])
        self.assertEqual(1, vote[0][3])

    def test_r_i_matrices(self):
        vote = client_util.create_vote([4, 2, 1, 3])
        secret_shared_matrices = util.partition_and_secret_share_vote(vote, local_servers)
        res = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        for matrix in secret_shared_matrices:
            for i, row in enumerate(matrix):
                for j, value in enumerate(row):
                    res[i][j] += value
                    res[i][j] %= util.get_prime()
        self.assertTrue(np.array_equal(vote, np.array(res)))

    def test_check_vote(self):
        vote = client_util.create_vote([4, 2, 1, 3])
        ss_vote_partitions = util.partition_and_secret_share_vote(vote, local_servers)
        res = 0
        for ss_partition in ss_vote_partitions:
            res =(res + server_util.create_sum_of_row(ss_partition)) % util.get_prime()
        self.assertTrue(server_util.check_rows_and_columns(res))

    def test_check_vote_neg(self):
        vote = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 1]])
        ss_vote_partitions = util.partition_and_secret_share_vote(vote, local_servers)
        res = 0
        for ss_partition in ss_vote_partitions:
            res = (res + server_util.create_sum_of_row(ss_partition)) % util.get_prime()
        self.assertFalse(server_util.check_rows_and_columns(res))


    def test_row_sum(self):
        r1 = (np.array([0, 0, 0, 1]), 0, "row", 'c1')
        r2 = (np.array([0, 0, 1, 0]), 1, "row", 'c1')
        r3 = (np.array([0, 1, 0, 0]), 2, "row", 'c1')
        r4 = (np.array([1, 0, 0, 0]), 3, "row", 'c1')
        illegal_votes = server_util.verify_sums([r1, r2, r3, r4], "5000")
        self.assertEqual(set(), illegal_votes)


    def test_neg_row_sum(self):
        r1 = (np.array([1,1,1,1]),0,"row", 'c1')
        r2 = (np.array([0,0,0,1]),1,"row", 'c1')
        r3 = (np.array([1,1,1,1]),2,"row", 'c1')
        illegal_votes = server_util.verify_sums([r1,r2,r3], "5000")
        self.assertEqual({'c1'}, illegal_votes)

    def test_create_sum_of_row(self):
        vote = client_util.create_vote([2, 1, 3, 4])
        summed_rows = server_util.create_sum_of_row(vote)
        for sum in summed_rows:
            self.assertEqual(1, sum)

    def test_create_sum_of_col_neg(self):
        vote = client_util.create_vote([1, 1, 3, 4])
        summed_rows = server_util.create_sum_of_row(vote.T)
        self.assertNotEqual(1, summed_rows[0])
        self.assertEqual(2, summed_rows[0])

    def test_single_vote(self):
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        for server in local_servers:
            util.get_url(server + "/zero_one_consistency")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + "/sumdifferenceshareforzeroone")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/check_votes')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/ensure_vote_agreement')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/add')
        time.sleep(1)
        for server in local_servers:
            response = util.get_url(server + '/compute_result')
            self.assertTrue(response.text=="ok")
        time.sleep(1)
        v = np.array([[0, 0, 0, 1],[0, 1, 0, 0],[1, 0, 0, 0],[0, 0, 1, 0]])
        for server in local_servers:
            response = util.get_url(server + '/verify_result')
            result = util.string_to_vote(response.text)
            self.assertTrue(np.array_equal(result, np.array(
                [sum([v[i][j] * (1 / (j + 1)) for j in range(v.shape[0])]) for i in range(v.shape[1])])))
            
    def test_adding_votes(self):
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c2', local_servers)
        # Bad vote
        client_util.send_vote([1, 1, 1, 1], 'c3', local_servers)
        client_util.send_vote([2, 2, 2, 2], 'c4', local_servers)
        for server in local_servers:
            util.get_url(server + "/zero_one_consistency")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + "/sumdifferenceshareforzeroone")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/check_votes')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/ensure_vote_agreement')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/add')
        time.sleep(1)
        for server in local_servers:
            response = util.get_url(server + '/compute_result')
            self.assertTrue(response.text=="ok")
        time.sleep(1)
        v = np.array([[1, 0, 0, 1],[0, 2, 0, 0],[1, 0, 1, 0],[0, 0, 1, 1]])
        for server in local_servers:
            response = util.get_url(server + '/verify_result')
            result = util.string_to_vote(response.text)
            self.assertTrue(np.array_equal(result, np.array(
                [sum([v[i][j] * (1 / (j + 1)) for j in range(v.shape[0])]) for i in range(v.shape[1])])))

    def test_receipt_freeness(self):
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c1', local_servers)
        for server in local_servers:
            util.get_url(server + "/zero_one_consistency")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + "/sumdifferenceshareforzeroone")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/check_votes')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/ensure_vote_agreement')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/add')
        time.sleep(1)
        for server in local_servers:
            response = util.get_url(server + '/compute_result')
            self.assertTrue(response.text=="ok")
        time.sleep(1)
        v = np.array([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1, 0],[0, 0, 0, 1]])
        for server in local_servers:
            response = util.get_url(server + '/verify_result')
            result = util.string_to_vote(response.text)
            self.assertTrue(np.array_equal(result, np.array(
                [sum([v[i][j] * (1 / (j + 1)) for j in range(v.shape[0])]) for i in range(v.shape[1])])))

    def test_new_product(self):
        illegal_vote = np.array([[3,-2],[-2,3]])
        illegal_vote_partitions = util.partition_and_secret_share_vote(illegal_vote, local_servers)
        client_util.postvote("ic3", illegal_vote_partitions, local_servers)
        client_util.send_vote([1,2], 'c1', local_servers)
        client_util.send_vote([2,1], 'c2', local_servers)
        illegal_vote = np.array([[2, -1], [-1, 2]])
        illegal_vote_partitions = util.partition_and_secret_share_vote(illegal_vote, local_servers)
        client_util.postvote("ic4", illegal_vote_partitions, local_servers)
        illegal_vote = np.array([[0, 0], [0, 0]])
        illegal_vote_partitions = util.partition_and_secret_share_vote(illegal_vote, local_servers)
        client_util.postvote("ic5", illegal_vote_partitions, local_servers)
        for server in local_servers:
            util.get_url(server + "/zero_one_consistency")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + "/sumdifferenceshareforzeroone")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/check_votes')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/ensure_vote_agreement')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/add')
        time.sleep(1)
        for server in local_servers:
            response = util.get_url(server + '/compute_result')
            self.assertTrue(response.text=="ok")
        time.sleep(1)
        for server in local_servers:
            response = util.get_url(server + '/verify_result')
            result = util.string_to_vote(response.text)
            self.assertTrue(np.array_equal(np.array([1.5,1.5]),result))

    def test_many_votes(self):
        reset_servers()
        for i in range(40):
            client = 'c' + str(i)
            client_util.send_vote([1, 2, 3, 4], client, local_servers)
        for server in local_servers:
            util.get_url(server + "/zero_one_consistency")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + "/sumdifferenceshareforzeroone")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/check_votes')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/ensure_vote_agreement')
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + '/add')
        time.sleep(1)
        for server in local_servers:
            response = util.get_url(server + '/compute_result')
            self.assertTrue(response.text=="ok")
        time.sleep(1)
        v = np.array([[10, 0, 0, 0], [0, 10, 0, 0], [0, 0, 10, 0], [0, 0, 0, 10]])
        for server in local_servers:
            response = util.get_url(server + '/verify_result')
            result = util.string_to_vote(response.text)
            self.assertTrue(np.array_equal(result, np.array(
                [sum([v[i][j] * (1 / (j + 1)) for j in range(v.shape[0])]) for i in range(v.shape[1])])))

    @classmethod
    def tearDownClass(cls):
        for i in local_servers:
            requests.get(i + "/shutdown")
        requests.get(mediator + "/shutdown")
        time.sleep(1)


class TestMediator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile("cryp/publicmediator.pem"):
            util.get_keys("mediator")

        create_local_mediator(5100)

        time.sleep(3)

    def test_todo(self):
        server_util.send_illegal_votes_to_mediator([], "me", mediator, "test1")
        self.assertTrue(True)

    def test_message_inconsistency(self):
        for num, server in enumerate(local_servers):
            util.post_url(dict(complaint=util.vote_to_string(util.Complaint(
                server, dict(test="test1"), util.Protocol.check_votes, num+1 % 4
            )), server=server, sender=server.split(":")[-1]), mediator + "/messageinconsistency")
        time.sleep(0.2)
        print(requests.get(mediator + "/test/printcomplaints"))


    @classmethod
    def tearDownClass(cls):
        requests.get(mediator + "/shutdown")


class TestCheater(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for n in test_keys_necessary:
            if not os.path.isfile("cryp/public{}.pem".format(n)):
                util.get_keys(n)

        for i in range(3):
            create_local_server(5000 + i)
        create_local_mediator(5100)

        time.sleep(3)

    @classmethod
    def setUp(cls):
        reset_servers_not_cheater()

    @classmethod
    def tearDown(cls):
        requests.get(baseurl4 + "/shutdown")
        time.sleep(0.5)
        
    def test_row_sum(self):
        create_local_cheating_server(5003, [0, 1], 1)
        time.sleep(1)
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c2', local_servers)
        for s in local_servers:
            response = util.get_url(s + '/check_votes')
        self.assertTrue(len(requests.get(mediator + "/test/printcomplaints").text) > 2)

    def test_row_sum_neg(self):
        create_local_server(5003)
        time.sleep(1)
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c2', local_servers)
        for s in local_servers:
            response = util.get_url(s + '/check_votes')
        self.assertTrue(len(requests.get(mediator + "/test/printcomplaints").text) <= 2, msg=requests.get(mediator + "/test/printcomplaints").text)

    def test_cheat_final_result(self):
        create_local_cheating_server(5003, [0], 5)
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c2', local_servers)
        for s in local_servers:
            response = util.get_url(s + '/check_votes')
        for s in local_servers:
            response = util.get_url(s + '/ensure_vote_agreement')
        for server in local_servers:
            util.get_url(server + '/add')
        time.sleep(.5)
        for s in local_servers:
            response = util.get_url(s + '/compute_result')
        time.sleep(.5)
        for s in local_servers:
            response = util.get_url(s + "/verify_result")
            self.assertFalse(response.ok, msg="Servers don't agree on result, " + response.text)
        self.assertTrue(len(requests.get(mediator + "/test/printcomplaints").text) > 2)

        
    @classmethod
    def tearDownClass(cls):
        for i in local_servers[:-1]:
            requests.get(i + "/shutdown")
        requests.get(mediator + "/shutdown")
        time.sleep(1)

        

def reset_servers():
    for server in local_servers:
        requests.post(server + "/reset")
    requests.post(mediator + "/reset")


def reset_servers_not_cheater():
    for server in local_servers[:-1]:
        requests.post(server + "/reset")
    requests.post(mediator + "/reset")


if __name__ == '__main__':
    unittest.main()
    
