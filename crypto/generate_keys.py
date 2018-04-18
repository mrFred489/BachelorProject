import rsa

# crypto doc: https://stuvel.eu/files/python-rsa-doc/usage.html#signing-and-verification


# (pub, priv) = rsa.newkeys(2048)
#
# print(pub)
# print()
# print(priv)
#
# with open('public.pem', mode='wb') as privatefile:
#     privatefile.write(pub.save_pkcs1())
#
#
# with open('private.pem', mode='wb') as privatefile:
#     privatefile.write(priv.save_pkcs1())


with open('private.pem', mode='rb') as privatefile, open("public.pem", mode="rb") as publicfile:
    keydata1 = privatefile.read()
    keydata2 = publicfile.read()
privkey = rsa.PrivateKey.load_pkcs1(keydata1)
pubkey = rsa.PublicKey.load_pkcs1(keydata2)

message = 'Hej med dig'
print("message:", message)
signature = rsa.sign(message.encode(), privkey, 'SHA-1')
print("signature:", signature)
print("verify", rsa.verify(message.encode(), signature, pubkey))


