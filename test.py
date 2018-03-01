import util
import requests
import unittest
import time
from Client import client_util
import subprocess
import multiprocessing as mp
import os

p = util.get_prime()
baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"
baseurl3 = "http://127.0.0.1:5002/"

official_server = "https://cryptovoting.dk/"
official_server1 = "https://server1.cryptovoting.dk/"
official_server2 = "https://server2.cryptovoting.dk/"
official_server3 = "https://server3.cryptovoting.dk/"
official_server4 = "https://server4.cryptovoting.dk/"

n_servers = [baseurl1, baseurl2,
             official_server, official_server1,
             official_server2, official_server3, official_server4]

def create_server(port):
    #subprocess.run('python3 Server/routes.py ' + port, shell=True)
    os.system("Server/routes.py " + str(port))


def create_local_server(port):
    pr = mp.Process(target=create_server, args=(str(port), ))
    pr.start()


class test_arithmetics(unittest.TestCase):

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


class test_communication(unittest.TestCase):

    def setUpClass():
        create_local_server(5000)
        create_local_server(5001)
        create_local_server(5002)

        time.sleep(5)

    def test_multiple_servers(self):
        # Husk at starte to servere, med hver deres port nummer.
        servers = [baseurl1 + "server",
                   baseurl2 + "server",
                   baseurl3 + "server"]

        requests.post(baseurl1 + "reset")
        requests.post(baseurl2 + "reset")
        requests.post(baseurl3 + "reset")

        client_util.create_and_post_secret_to_servers(20, "x", servers)
        client_util.create_and_post_secret_to_servers(12, "x", servers)
        client_util.create_and_post_secret_to_servers(18, "x", servers)

        total = client_util.getTotal([baseurl1, baseurl2, baseurl3])

        self.assertEqual(50, total)

    def test_n_official_servers(self):
        servers = [server + "server" for server in n_servers]

        reset_servers()

        client_util.create_and_post_secret_to_servers(28, "x", servers)
        client_util.create_and_post_secret_to_servers(22, "y", servers)

        time.sleep(0.1)

        total = client_util.getTotal(n_servers)

        self.assertEqual(50, total % util.get_prime())

    def tearDownClass():
        requests.get(baseurl1 + "shutdown")
        requests.get(baseurl2 + "shutdown")
        requests.get(baseurl3 + "shutdown")


def reset_servers():
    for server in n_servers:
        requests.post(server + "reset")


if __name__ == '__main__':
    unittest.main()



