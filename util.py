import numpy as np
import requests
import random
import codecs
import pickle
import rsa
import rsa.pkcs1
import cryp.keys
import json


privkey = None
pubkey = None


def get_keys(name):
    global privkey, pubkey
    if None not in [privkey, pubkey]:
        return
    privkey, pubkey = cryp.keys.get_key(name)


def get_prime():
    return 50


def make_post_signature(data):
    dump = json.dumps(data)
    signature = rsa.sign(dump.encode(), privkey, "SHA-1")
    return {"data": dump, "signature": bytearray(signature), "pub": pubkey.save_pkcs1()}


def post_url(data: dict, url: str):
    return requests.post(url, make_post_signature(data))


def verify(sig, data, pub):
    try:
        if type(pub) == str:
            pub = rsa.PublicKey.load_pkcs1(pub)
        return rsa.verify(data.encode(), sig, pub)
    except rsa.pkcs1.VerificationError:
        return False


def get_url(url):
    response = requests.get(url)
    return response


def vote_to_string(vote):
    return codecs.encode(pickle.dumps(vote), "base64").decode()


def string_to_vote(string_vote):
    return pickle.loads(codecs.decode(string_vote.encode(), "base64"))


def create_addition_secret(x: int, n: int):
    p = get_prime()
    rng = random.Random()
    res = []
    for i in range(n - 1):
        res.append(rng.randrange(0, p - 1, 1))
    res.append((x - sum(res)) % get_prime())
    return res


def partition_and_secret_share_vote(vote: np.ndarray, servers: list):
    ###
    r_i_matrices = []
    amount_of_servers = len(servers)
    for i in range(amount_of_servers):
        r_i_matrices.append([])
        for row in vote:
            r_i_matrices[i].append([])

    for i, row in enumerate(vote):
        for value in row:
            curr_secret = create_addition_secret(value, amount_of_servers)
            for j, s in enumerate(curr_secret):
                r_i_matrices[j][i].append(s)

    temp = []
    for i in r_i_matrices:
        temp.append(np.array(i))
    return temp

