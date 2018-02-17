import util
import requests
import unittest

baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"
p = 4000001

# class test_arithmetics(unittest.TestCase):
#
#     def test_addition(self):
#         x = util.create_secret(22, 100, 3)
#         y = util.create_secret(28, 100, 3)
#         res = sum(x) + sum(y)
#         self.assertEqual(int(res), 50)
#

official_server = "https://cryptovoting.dk/"
official_server1 = "https://server1.cryptovoting.dk/"

n_servers = [baseurl1, baseurl2, official_server, official_server1]

class test_arithmetics(unittest.TestCase):



class test_communication(unittest.TestCase):

    def test_multiple_servers(self):
        # Husk at starte to servere, med hver deres port nummer.
        servers = [baseurl1 + "server0", baseurl2 + "server0"]

        requests.post(baseurl1 + "reset")
        requests.post(baseurl2 + "reset")

        util.create_and_post_secret_to_servers(28, 100, "x", servers)
        util.create_and_post_secret_to_servers(22, 100, "x", servers)

        total = util.getTotal([baseurl1, baseurl2])
        # num1 = requests.get(baseurl1 + "total").text
        # num2 = requests.get(baseurl2 + "total").text
        # p = util.get_prime(baseurl1 + "server0" + '/prime')
        self.assertEqual(total, 50)
        # print(num1, "+", num2, "=", int(num1) + int(num2))
        # print("database1:", requests.get(baseurl1 + "databases").text)
        # print("database2:", requests.get(baseurl2 + "databases").text)

    def test_n_official_servers(self):
        servers = [server + "server0" for server in n_servers]

        for server in n_servers:
            requests.post(server + "reset")

        util.create_and_post_secret_to_servers(28, 100, "x", servers)
        util.create_and_post_secret_to_servers(22, 100, "y", servers)

        total = 0

        for server in n_servers:
            total += int(requests.get(server + "total").text)

        self.assertEqual(total, 50)




if __name__ == '__main__':
    unittest.main()
