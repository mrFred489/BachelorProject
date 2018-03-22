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
baseurl4 = "http://127.0.0.1:5003/"
baseurl5 = "http://127.0.0.1:5004/"

local_servers = [baseurl1, baseurl2, baseurl3,baseurl4, baseurl5]

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
        for i in range(5):
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

    def test_adding_votes(self):
        reset_servers()
        client_util.send_vote([4, 2, 1, 3], 'c1', local_servers)
        client_util.send_vote([1, 2, 3, 4], 'c2', local_servers)
        for server in local_servers:
            util.get_url(server + 'add')
        for s in local_servers:
            response = util.get_url(s + 'compute_result')
            self.assertTrue(np.array_equal(util.string_to_vote(response.text), np.array([
                                                                                            [1, 0, 0, 1],
                                                                                            [0, 2, 0, 0],
                                                                                            [1, 0, 1, 0],
                                                                                            [0, 0, 1, 1]])))
            self.assertTrue(response.ok)

    def test_neg_row_sum(self):
        r1 = (np.array([1,1,1,1]),0,"row", 'c1')
        r2 = (np.array([0,0,0,1]),1,"row", 'c1')
        r3 = (np.array([1,1,1,1]),2,"row", 'c1')
        illegal_votes = server_util.verify_sums([r1,r2,r3])
        self.assertTrue('c1' in illegal_votes)


    # TODO: add test that checks that server actually sorts away illegal votes

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

    def test_division_of_secret_shares(self):
        to_send_to = client_util.divide_secret_shares(len(local_servers))
        for i in range(len(local_servers)):
            partition_for_server = to_send_to[i]
            self.assertTrue((i not in partition_for_server))

    # def test_many_votes(self):
    #     reset_servers()
    #     for i in range(1000):
    #         client = 'c' + str(i)
    #         client_util.send_vote([4, 2, 1, 3], client, local_servers)
    #         # client_util.send_vote([1, 2, 3, 4], 'c2', local_servers)
    #     for server in local_servers:
    #         util.get_url(server + 'add')
    #     for s in local_servers:
    #         response = util.get_url(s + 'compute_result')
    #         print("RES IS: ", util.string_to_vote(response.text))




    @classmethod
    def tearDownClass(cls):
        for i in local_servers:
            requests.get(i + "shutdown")



def reset_servers():
    for server in n_servers:
        requests.post(server + "reset")


if __name__ == '__main__':
    unittest.main()
