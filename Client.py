import socket
from _pickle import dumps, loads
from base64 import b64decode, b64encode
from Encryption import *
from Crypto.PublicKey import RSA
import os
from time import sleep

IP = "localhost"
PORT = 6666
ADDRESS = (IP, PORT)
INTERRUPT = b"/S/s0101s/S/"


class Client:
    def __init__(self):
        self.socket = socket.socket()
        self.socket.connect(ADDRESS)
        # receive RSA key
        self.public_key = RSA.import_key(self.socket.recv(2056))
        # diffie helmen
        self.diffie = DiffieUtil()
        self.key = self.diffie.recv(self.socket)
        self.diffie.send(self.socket, self.public_key)

    def send_file(self, path):
        file_name = os.path.split(path)[-1]
        path = AesUtil.encrypt_file(path, self.key)
        self.socket.send(pack_int(1))
        sleep(0.5)
        self.socket.send(file_name.encode("utf8"))
        sleep(0.5)
        with open(path, 'rb') as f:
            data = f.read(2056)
            while data:
                self.socket.send(data)
                data = f.read(2056)
        self.socket.send(INTERRUPT)  # send an interrupt
