import rsa

def get_key(name):
    try:
        with open("cryp/private{}.pem".format(name), mode='rb') as privatefile, open("cryp/public{}.pem".format(name), mode="rb") as publicfile:
            keydata1 = privatefile.read()
            keydata2 = publicfile.read()
            privkey = rsa.PrivateKey.load_pkcs1(keydata1)
            pubkey = rsa.PublicKey.load_pkcs1(keydata2)

    except:
        (pubkey, privkey) = rsa.newkeys(512)
        with open("cryp/public{}.pem".format(name), mode='wb') as publicfile, open("cryp/private{}.pem".format(name), mode='wb') as privatefile:
            publicfile.write(pubkey.save_pkcs1())
            privatefile.write(privkey.save_pkcs1())
    return privkey, pubkey

def get_public_key(name):
    pubkey = None
    try:
        with open("cryp/public{}.pem".format(name), mode="rb") as publicfile:
            keydata2 = publicfile.read()
            pubkey = rsa.PublicKey.load_pkcs1(keydata2)

    except:
        print("missing public key for {}".format(name))
    return pubkey