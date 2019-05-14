import socket
from _pickle import dumps, loads
from base64 import b64decode, b64encode

IP = "localhost"
PORT = 5678
ADDRESS = (IP, PORT)


class Client:
    def __init__(self):
        self.socket = socket.socket()
        #self.socket.connect(ADDRESS)