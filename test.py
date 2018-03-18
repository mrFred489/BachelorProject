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


p = util.get_prime()
baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"
baseurl3 = "http://127.0.0.1:5002/"

local_servers = [baseurl1, baseurl2, baseurl3]

official_server = "https://cryptovoting.dk/"
official_server1 = "https://server1.cryptovoting.dk/"
official_server2 = "https://server2.cryptovoting.dk/"
official_server3 = "https://server3.cryptovoting.dk/"
official_server4 = "https://server4.cryptovoting.dk/"

n_servers = [baseurl1, baseurl2, baseurl3,
             official_server, official_server1,
             official_server2, official_server3, official_server4]


def create_local_server(port):
    pr = mp.Process(target=Server.routes.create_local, args=(str(port),))
    pr.start()


class TestArithmetics(unittest.TestCase):

    def test_addition(self):
        secrets_1 = util.create_addition_secret(10, 2)
        secrets_2 = util.create_addition_secret(15, 2)
        res = (sum(secrets_1) + sum(secrets_2)) % util.get_prime()
        self.assertEqual(25, res)



class TestCommunication(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for i in range(3):
            create_local_server(5000 + i)

        time.sleep(3)

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
        self.assertTrue(server_util.check_rows_and_columns(vote))

    def neg_test_check_vote(self):
        vote = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 1]])
        self.assertFalse(server_util.check_rows_and_columns(vote))


    def test_adding_votes(self):
        reset_servers()
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c2', local_servers)
        for server in local_servers:
            util.get_url(server + 'add')
        for s in local_servers:
            response = util.get_url(s + 'compute_result')
            self.assertTrue(np.array_equal(util.string_to_vote(response.text), np.array([[1, 0, 0, 1],
                                                                                            [0, 2, 0, 0],
                                                                                            [1, 0, 1, 0],
                                                                                            [0, 0, 1, 1]])))
            self.assertTrue(response.ok)

    def test_retrieving_votes_from_database(self):
        pass

    @classmethod
    def tearDownClass(cls):
        for i in local_servers:
            requests.get(i + "shutdown")



def reset_servers():
    for server in n_servers:
        requests.post(server + "reset")


if __name__ == '__main__':
    unittest.main()
