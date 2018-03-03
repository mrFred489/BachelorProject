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
        secrets_1 = client_util.create_addition_secret(10, 2, baseurl1 + 'server')
        secrets_2 = client_util.create_addition_secret(15, 2, baseurl2 + 'server')
        res = sum(secrets_1) + sum(secrets_2)
        self.assertEqual(25, res)

    def test_multiplication(self):
        secrets_1 = client_util.create_multiplication_secret(5, 2)
        secrets_2 = client_util.create_multiplication_secret(5, 2)
        res = 0
        for x in secrets_1:
            for y in secrets_2:
                res += x * y
        self.assertEqual(25, res)

    def test_multiplication2(self):
        secrets_1 = client_util.create_multiplication_secret(p - 1, 2)
        secrets_2 = client_util.create_multiplication_secret(p - 1, 2)
        res = 0
        for x in secrets_1:
            for y in secrets_2:
                res += x * y
        self.assertEqual((p - 1) * (p - 1), res)


class TestCommunication(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        for i in range(3):
            create_local_server(5000 + i)

        time.sleep(3)

    def test_multiple_servers(self):
        # Husk at starte to servere, med hver deres port nummer.

        reset_servers()

        client_util.create_and_post_secret_to_servers(20, "c1", local_servers)
        client_util.create_and_post_secret_to_servers(12, "c2", local_servers)
        client_util.create_and_post_secret_to_servers(18, "c3", local_servers)

        total = client_util.get_total(local_servers)

        self.assertEqual(50, total)

    def test_n_official_servers(self):
        # servers = [server + "server" for server in n_servers]

        reset_servers()
        client_util.create_and_post_secret_to_servers(28, "c1", n_servers)
        client_util.create_and_post_secret_to_servers(22, "c2", n_servers)

        time.sleep(0.1)

        total = client_util.get_total(n_servers)

        self.assertEqual(50, total % util.get_prime())


    def test_server_calculation_of_sum(self):
        reset_servers()

        client_util.create_and_post_secret_to_servers(28, "c3", local_servers)
        client_util.create_and_post_secret_to_servers(11, "c4", local_servers)
        client_util.create_and_post_secret_to_servers(10, "c5", local_servers)
        client_util.create_and_post_secret_to_servers(1, "c6", local_servers)

        client_util.voting_done(local_servers)
        s = requests.get(baseurl1 + 'compute_result').json()['s'] % util.get_prime()

        self.assertEqual(50, s)

    def test_check_of_si_values(self):
        reset_servers()

        client_util.create_and_post_secret_to_servers(28, "c3", local_servers)
        client_util.create_and_post_secret_to_servers(11, "c4", local_servers)
        client_util.create_and_post_secret_to_servers(10, "c5", local_servers)
        client_util.create_and_post_secret_to_servers(1, "c6", local_servers)

        server_util.send_value_to_server(5, 's', 1, baseurl2, baseurl1 + 'server')

        client_util.voting_done(local_servers)

        s = requests.get(baseurl1 + 'compute_result').json()['s']

        self.assertEqual('Database corrupted', s)

    @classmethod
    def tearDownClass(cls):
        for i in local_servers:
            requests.get(i + "shutdown")



def reset_servers():
    for server in n_servers:
        requests.post(server + "reset")


if __name__ == '__main__':
    unittest.main()
