import util
import requests
import unittest
import time
from Client import client_util
import multiprocessing as mp
import Server.routes
from Server import server_util
from time import sleep

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
        res = sum(secrets_1) + sum(secrets_2)
        self.assertEqual(25, res)



class TestCommunication(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for i in range(3):
            create_local_server(5000 + i)

        time.sleep(3)

    def test_vote_format(self):
        vote = client_util.create_vote('c1', [4, 2, 1, 3])
        self.assertEqual(1, vote[0][3])

    def test_r_i_matrices(self):
        vote = client_util.create_vote('c1', [4, 2, 1, 3])
        secret_shared_matrices = client_util.secret_share_priority_matrix(vote, local_servers)
        res = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for matrix in secret_shared_matrices:
            for i, row in enumerate(matrix):
                for j, value in enumerate(row):
                    res[i][j] += value
                    res[i][j] %= util.get_prime()
        print("VOTE IS: ", vote)
        print("RESS IS: ", res)
        self.assertListEqual(vote,res)

    # def test_sending_votes(self):
    #     vote = client_util.create_vote('c1', [4, 2, 1, 3])
    #     client_util.send_matrix_vote('c1', vote, local_servers)

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
