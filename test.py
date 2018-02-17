import util
import requests
import unittest

baseurl1 = "http://127.0.0.1:5000/"
baseurl2 = "http://127.0.0.1:5001/"

class test_arithmetics(unittest.TestCase):

    def test_addition(self):
        x = util.create_secret(22, 100, 3)
        y = util.create_secret(28, 100, 3)
        res = sum(x) + sum(y)
        self.assertEqual(int(res), 50)

class test_communication(unittest.TestCase):

    def test_multiple_servers(self):
        # Husk at starte to servere, med hver deres port nummer.
        # Note that currently this test will fail if anything has already been submitted to the servers 'database' - e.g by running the tests twice
        servers = [baseurl1 + "server0", baseurl2 + "server0"]
        util.create_and_post_secret_to_servers(28, 100, "x", servers)
        util.create_and_post_secret_to_servers(22, 100, "x", servers)

        num1 = requests.get(baseurl1).text
        num2 = requests.get(baseurl2).text

        # print(num1, "+", num2, "=", int(num1) + int(num2))
        self.assertEqual(50, int(num1) + int(num2))
        # print("database1:", requests.get(baseurl1 + "databases").text)
        # print("database2:", requests.get(baseurl2 + "databases").text)


if __name__ == '__main__':
    unittest.main()
