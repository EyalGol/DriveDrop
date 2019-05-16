import socket
from _pickle import dumps, loads
from base64 import b64decode, b64encode
from Encryption import *
from Crypto.PublicKey import RSA
import os

IP = "localhost"
PORT = 6669
ADDRESS = (IP, PORT)
SPECIAL_CHARS = {"interrupt": b"/i0101i/", "recv_file_command": b"/r0101f/", "continue": b"/n0101n/",
                 "authenticate": b"/a0101a/", "list_files": b"/r0101r/"}


class Client:
    def __init__(self):
        self.socket = None
        self.public_key = None
        self.diffie = None
        self.key = None
        self.groups = None
        self.init_connection()

    def init_connection(self):
        try:
            self.socket = socket.socket()
            self.socket.connect(ADDRESS)
            # receive RSA key
            self.public_key = RSA.import_key(self.socket.recv(2056))
            # diffie helmen
            self.diffie = DiffieUtil()
            self.key = self.diffie.recv(self.socket)
            self.diffie.send(self.socket, self.public_key)
        except ConnectionAbortedError or ConnectionResetError:
            self.init_connection()

    def send_file(self, path, last=True):
        try:
            file_name = os.path.split(path)[-1].encode("utf8")
            path = AesUtil.encrypt_file(path, self.key)
            self.socket.send(SPECIAL_CHARS["recv_file_command"])
            self.socket.recv(128)
            self.socket.send(file_name)
            self.socket.recv(128)
            with open(path, 'rb') as f:
                print("sending file...")
                data = f.read(2056)
                while data:
                    self.socket.send(data)
                    data = f.read(2056)
            self.socket.send(SPECIAL_CHARS["interrupt"])
            self.socket.recv(128)
            if last:
                self.socket.send(SPECIAL_CHARS["interrupt"])
            else:
                self.socket.send(SPECIAL_CHARS["continue"])
                self.socket.recv(128)
            os.remove(path)
            return True
        except ConnectionAbortedError or ConnectionResetError:
            self.socket.close()
            self.init_connection()

    def login(self, username, password):
        try:
            self.socket.send(SPECIAL_CHARS["authenticate"])
            self.socket.recv(128)
            self.socket.send(AesUtil.encrypt_login(username, password, self.key))
            groups = loads(self.socket.recv(2056))
            if groups:
                self.groups = groups
            return groups
        except ConnectionAbortedError or ConnectionResetError:
            self.socket.close()
            self.init_connection()

    def get_file_list(self):
        return ["idk", "idc"]