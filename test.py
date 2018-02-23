import util
import requests
import unittest
import time

p = 4000001
baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"
baseurl3 = "http://127.0.0.1:5002/"

official_server = "https://cryptovoting.dk/"
official_server1 = "https://server1.cryptovoting.dk/"
official_server2 = "https://server2.cryptovoting.dk/"
official_server3 = "https://server3.cryptovoting.dk/"
official_server4 = "https://server4.cryptovoting.dk/"

n_servers = [baseurl1, baseurl2, official_server, official_server1, official_server2, official_server3, official_server4]



class test_arithmetics(unittest.TestCase):

    def test_addition(self):
        secrets_1 = util.create_addition_secret(10, 2, baseurl1 + 'server')
        secrets_2 = util.create_addition_secret(15, 2, baseurl2 + 'server')
        res = sum(secrets_1) + sum(secrets_2)
        self.assertEqual(25, res)

 ##TODO: make partitioning of numbers for multiplication (split the number into amount _of_servers parts)
    def test_multiplication(self):
        secrets_1 = util.create_multiplication_secret(5, 2)
        secrets_2 = util.create_multiplication_secret(5, 2)
        res = 0
        for x in secrets_1:
            for y in secrets_2:
                res += x * y
        self.assertEqual(25, res)


class test_communication(unittest.TestCase):

    def test_multiple_servers(self):
        # Husk at starte to servere, med hver deres port nummer.
        servers = [baseurl1 + "server", baseurl2 + "server", baseurl3 + "server"]

        requests.post(baseurl1 + "reset")
        requests.post(baseurl2 + "reset")
        requests.post(baseurl3 + "reset")

        util.create_and_post_secret_to_servers(20, "x", servers)
        util.create_and_post_secret_to_servers(12, "x", servers)
        util.create_and_post_secret_to_servers(18, "x", servers)

        total = util.getTotal([baseurl1, baseurl2, baseurl3])

        self.assertEqual(50, total)

    def test_n_official_servers(self):
        servers = [server + "server" for server in n_servers]

        reset_servers()

        util.create_and_post_secret_to_servers(28, "x", servers)
        util.create_and_post_secret_to_servers(22, "y", servers)

        time.sleep(0.1)

        total = util.getTotal(n_servers)

        self.assertEqual(50, total % util.get_prime(servers[0]))


def reset_servers():
    for server in n_servers:
        requests.post(server + "reset")


if __name__ == '__main__':
    unittest.main()
