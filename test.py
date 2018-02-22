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


# class test_arithmetics(unittest.TestCase):
#
#     def test_addition(self):
#         x = util.create_secret(22, 100, 3)
#         y = util.create_secret(28, 100, 3)
#         res = sum(x) + sum(y)
#         self.assertEqual(int(res), 50)
#

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
        # num1 = requests.get(baseurl1 + "total").text
        # num2 = requests.get(baseurl2 + "total").text
        # p = util.get_prime(baseurl1 + "server" + '/prime')
        self.assertEqual(50, total)
        # print(num1, "+", num2, "=", int(num1) + int(num2))
        # print("database1:", requests.get(baseurl1 + "databases").text)
        # print("database2:", requests.get(baseurl2 + "databases").text)

    def test_n_official_servers(self):
        servers = [server + "server" for server in n_servers]

        reset_servers()

        util.create_and_post_secret_to_servers(28, "x", servers)
        util.create_and_post_secret_to_servers(22, "y", servers)

        time.sleep(0.1)

        total = util.getTotal(n_servers)

        # for server in n_servers:
        #     total += int(requests.get(server + "total").text)

        self.assertEqual(50, total % util.get_prime(servers[0]))


def reset_servers():
    for server in n_servers:
        requests.post(server + "reset")


if __name__ == '__main__':
    unittest.main()
