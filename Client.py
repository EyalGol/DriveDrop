from random import randint

import requests
from Crypto.PublicKey import RSA

from Encryption import *
from Networking import *


class Client(Encryption, Networking):
    def __init__(self, address):
        Encryption.__init__(self, randint(10000, 1000000))
        Networking.__init__(self)
        self.address = address
        self.pub_key = RSA.import_key(requests.get('http://127.0.0.1:5000/key/')._content)

    def handshake(self, soc=None):
        base = 345
        mod = 286
        private = randint(100, 999)
        pk = self.diffie_algo(mod, base, private)
        print(1)
        self.socket = socket.socket()
        self.socket.connect(self.address)
        print(2)
        self.send_bytes("handshake".encode())

        data = self.recv_bytes()
        print(3)
        key = self.diffie_algo(mod, self.check_signature(data, self.pub_key), private)
        print(4)
        self.send_bytes(pk)
        return key


c = Client(("localhost", 6666))
if input("in: "):
    c.handshake()
