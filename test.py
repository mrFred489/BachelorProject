import util
import requests
import unittest
import time
from Client import client_util
import multiprocessing as mp
import Server.routes
from Server import server_util
from time import sleep
import numpy as np
import os.path
import Mediator.mediator


baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"
baseurl3 = "http://127.0.0.1:5002/"
baseurl4 = "http://127.0.0.1:5003/"
mediator = "http://127.0.0.1:5100/"

local_servers = [baseurl1, baseurl2, baseurl3,baseurl4]

local_servers_and_med = local_servers + [mediator]

official_server = "https://cryptovoting.dk/"
official_server1 = "https://server1.cryptovoting.dk/"
official_server2 = "https://server2.cryptovoting.dk/"
official_server3 = "https://server3.cryptovoting.dk/"
official_server4 = "https://server4.cryptovoting.dk/"

n_servers = [baseurl1, baseurl2, baseurl3,
             official_server, official_server1,
             official_server2, official_server3, official_server4]

test_keys_necessary = ["", "c1", "c2", "mediator"] + [str(5000+i) for i in range(5)]

def create_local_server(port):
    pr = mp.Process(target=Server.routes.create_local, args=(str(port),))
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

    def test_multiplication_x_minus_one(self):
        secret = [20, 1, 91, 13, 4, 2, 27]
        secret_real_sum = np.sum(secret) * (np.sum(secret) - np.array([[1]]))
        secret_share_sums = []
        for id in range(7):
            secret_share_sums.append(server_util.index_zero_one_check(id, 7, secret))
        self.assertEqual(round(sum(secret_share_sums)), secret_real_sum[0][0])

    def test_matrix_local_zero_one_check(self):
        vote = client_util.create_vote([1, 2, 3])
        secrets = util.partition_and_secret_share_vote(vote, local_servers)
        secrets_dict = dict()
        for i, secret in enumerate(secrets):
            secrets_dict[i] = secret
        secret_share_sum = []
        for id in range(len(local_servers)):
            secret_share_sum.append(server_util.matrix_zero_one_check(id, len(local_servers), secrets_dict, "server" + str(id), "test1")) # TODO: Korrekt client og my_name?
        val = server_util.zero_one_check(secret_share_sum)
        result = np.array_equal(val, np.zeros(val.shape))
        self.assertTrue(result)

    def test_matrix_local_zero_one_check_illegal(self):
        vote = np.array([[1, -2, 2],[0, 1, 0],[0, 2, -1]])
        secrets = util.partition_and_secret_share_vote(vote, local_servers)
        secrets_dict = dict()
        for i, secret in enumerate(secrets):
            secrets_dict[i] = secret
        secret_share_sum = []
        for id in range(len(local_servers)):
            secret_share_sum.append(server_util.matrix_zero_one_check(id, len(local_servers), secrets_dict))
        val = server_util.zero_one_check(secret_share_sum)
        result = np.array_equal(val, np.zeros(val.shape))
        self.assertFalse(result)

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

    def test_vote_format(self):
        reset_servers()
        vote = client_util.create_vote([4, 2, 1, 3])
        self.assertEqual(1, vote[0][3])

    def test_r_i_matrices(self):
        reset_servers()
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
        reset_servers()
        vote = client_util.create_vote([4, 2, 1, 3])
        ss_vote_partitions = util.partition_and_secret_share_vote(vote, local_servers)
        res = 0
        for ss_partition in ss_vote_partitions:
            res =(res + server_util.create_sum_of_row(ss_partition)) % util.get_prime()
        self.assertTrue(server_util.check_rows_and_columns(res))

    def test_check_vote_neg(self):
        reset_servers()
        vote = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 1]])
        ss_vote_partitions = util.partition_and_secret_share_vote(vote, local_servers)
        res = 0
        for ss_partition in ss_vote_partitions:
            res = (res + server_util.create_sum_of_row(ss_partition)) % util.get_prime()
        self.assertFalse(server_util.check_rows_and_columns(res))

    def test_row_sum(self):
        reset_servers()
        r1 = (np.array([0, 0, 0, 1]), 0, "row", 'c1')
        r2 = (np.array([0, 0, 1, 0]), 1, "row", 'c1')
        r3 = (np.array([0, 1, 0, 0]), 2, "row", 'c1')
        r4 = (np.array([1, 0, 0, 0]), 3, "row", 'c1')
        illegal_votes = server_util.verify_sums([r1, r2, r3, r4])
        self.assertEqual(set(), illegal_votes)


    def test_neg_row_sum(self):
        reset_servers()
        r1 = (np.array([1,1,1,1]),0,"row", 'c1')
        r2 = (np.array([0,0,0,1]),1,"row", 'c1')
        r3 = (np.array([1,1,1,1]),2,"row", 'c1')
        illegal_votes = server_util.verify_sums([r1,r2,r3])
        self.assertEqual({'c1'}, illegal_votes)


    # TODO: add test that checks that server actually sorts away illegal votes

    def test_create_sum_of_row(self):
        reset_servers()
        vote = client_util.create_vote([2, 1, 3, 4])
        summed_rows = server_util.create_sum_of_row(vote)
        for sum in summed_rows:
            self.assertEqual(1, sum)

    def test_create_sum_of_col_neg(self):
        reset_servers()
        vote = client_util.create_vote([1, 1, 3, 4])
        summed_rows = server_util.create_sum_of_row(vote.T)
        self.assertNotEqual(1, summed_rows[0])
        self.assertEqual(2, summed_rows[0])

    def test_division_of_secret_shares(self):
        reset_servers()
        to_send_to = client_util.divide_secret_shares()
        for i in range(len(local_servers)):
            partition_for_server = to_send_to[i]
            self.assertTrue((i not in partition_for_server))
            self.assertTrue((i+1) % len(local_servers) not in partition_for_server)

    def test_adding_votes(self):
        reset_servers()
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c2', local_servers)
        # Bad vote
        client_util.send_vote([1, 1, 1, 1], 'c3', local_servers)
        client_util.send_vote([2, 2, 2, 2], 'c4', local_servers)
        for s in local_servers:
            response = util.get_url(s + 'check_votes')
        for s in local_servers:
            response = util.get_url(s + 'ensure_vote_agreement')
        for server in local_servers:
            util.get_url(server + 'add')
        time.sleep(.5)
        for s in local_servers:
            response = util.get_url(s + 'compute_result')
            result = np.rint(util.string_to_vote(response.text))
            print(result)
            self.assertTrue(np.array_equal(result, np.array([[1, 0, 0, 1],
                                                             [0, 2, 0, 0],
                                                             [1, 0, 1, 0],
                                                             [0, 0, 1, 1]])))
            self.assertTrue(response.ok)

    def test_receipt_freeness(self):
        reset_servers()
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c1', local_servers)
        for s in local_servers:
            response = util.get_url(s + 'check_votes')
        for s in local_servers:
            response = util.get_url(s + 'ensure_vote_agreement')
        for server in local_servers:
            util.get_url(server + 'add')
        time.sleep(.5)
        for s in local_servers:
            response = util.get_url(s + 'compute_result')
            result = np.rint(util.string_to_vote(response.text))
            self.assertTrue(np.array_equal(result, np.array([[1, 0, 0, 0],
                                                             [0, 1, 0, 0],
                                                             [0, 0, 1, 0],
                                                             [0, 0, 0, 1]])))
            self.assertTrue(response.ok)

    def test_new_product(self):
        reset_servers()
        vote1 = client_util.create_vote([1])
        vote1_partitions = util.partition_and_secret_share_vote(vote1, local_servers)
        client_util.postvote("test1", vote1_partitions, local_servers)
        for server in local_servers:
            util.get_url(server + "zero_one_consistency")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + "sumdifferenceshareforzeroone")
        time.sleep(1)
        for server in local_servers:
            util.get_url(server + "zeroone_sum_partition_finalize")
        self.assertTrue(True)

    # def test_many_votes(self):
    #     reset_servers()
    #     for i in range(10):
    #         client = 'c' + str(i)
    #         client_util.send_vote([1, 2, 3, 4], client, local_servers)
    #     for server in local_servers:
    #         util.get_url(server + 'add')
    #     for s in local_servers:
    #         response = util.get_url(s + 'compute_result')
    #         self.assertTrue(np.array_equal(util.string_to_vote(response.text), np.array([
    #             [10, 0, 0, 0],
    #             [0, 10, 0, 0],
    #             [0, 0, 10, 0],
    #             [0, 0, 0, 10]])))
    #         self.assertTrue(response.ok)

    @classmethod
    def tearDownClass(cls):
        for i in local_servers:
            requests.get(i + "shutdown")
        requests.get(mediator + "shutdown")
        time.sleep(1)


class TestMediator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile("cryp/publicmediator.pem"):
            util.get_keys("mediator")

        create_local_mediator(5100)

        time.sleep(3)

    def test_todo(self):
        server_util.send_illegal_votes_to_mediator([], "me", mediator[:-1], "test1")
        self.assertTrue(True)

    @classmethod
    def tearDownClass(cls):
        requests.get(mediator + "shutdown")


def reset_servers():
    for server in local_servers:
        requests.post(server + "reset")
    requests.post(mediator + "reset")


if __name__ == '__main__':
    unittest.main()
