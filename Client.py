import socket
from _pickle import dumps, loads
from base64 import b64decode, b64encode
from Encryption import *
from Crypto.PublicKey import RSA
import os
import json

IP = "localhost"
PORT = 6667
ADDRESS = (IP, PORT)
SPECIAL_CHARS = {"interrupt": b"/i0101i/", "recv_file_command": b"/r0101f/", "continue": b"/n0101n/",
                 "authenticate": b"/a0101a/", "list_files": b"/l0101f/", "send_file": b"/r0101r/"}


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
        except ConnectionError:
            self.init_connection()

    def send_file(self, path, last=True):
        if "write" not in self.groups:
            return "INEFFICIENT PERMISSION"
        try:
            file_name = os.path.split(path)[-1]
            path = AesUtil.encrypt_file(path, self.key)
            self.socket.send(SPECIAL_CHARS["recv_file_command"])
            self.socket.recv(128)
            file_name, iv = AesUtil.encrypt_plaintext(file_name, self.key)
            self.socket.send(dumps((iv, file_name)))
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
            return "Success"
        except ConnectionError:
            self.socket.close()
            self.init_connection()
            return "Failed"
        except Exception as err:
            print(err)
            return "Failed"

    def login(self, username, password):
        try:
            self.socket.send(SPECIAL_CHARS["authenticate"])
            self.socket.recv(128)
            self.socket.send(AesUtil.encrypt_login(username, password, self.key))
            groups = loads(self.socket.recv(2056))
            if groups:
                self.groups = groups
            return groups
        except ConnectionError:
            self.socket.close()
            self.init_connection()
        except Exception as err:
            print(err)
            return "Failed"

    def get_file_list(self):
        try:
            if "view" not in self.groups:
                return ["INEFFICIENT PERMISSIONS"]
            self.socket.send(SPECIAL_CHARS["list_files"])
            iv = self.socket.recv(128)
            if SPECIAL_CHARS["interrupt"] not in iv:
                self.socket.send(SPECIAL_CHARS["continue"])
                enc_list = loads(self.socket.recv(5000))
                dec_list = []
                for file in enc_list:
                    dec_list.append(AesUtil.decrypt_plaintext(file, self.key, iv))
                return dec_list
            return ["No files found"]
        except ConnectionError:
            self.socket.close()
            self.init_connection()
            return "Failed"
        except Exception as err:
            print(err)
            return "Failed"

    def recv_files(self, file_name):
        if "retrieve" not in self.groups:
            return "INEFFICIENT PERMISSION"
        conn = self.socket
        try:
            key = self.key
            conn.send(SPECIAL_CHARS["send_file"])
            conn.recv(128)
            enc_file_name, iv = AesUtil.encrypt_plaintext(file_name, self.key)
            conn.send(dumps((iv, enc_file_name)))
            data = conn.recv(128)
            if data != SPECIAL_CHARS["continue"]:
                return data.decode()
            path = os.path.join(".", "tmp", "(cenc){}".format(file_name))
            with open(path, "wb") as f:
                print("receiving...")
                while True:
                    data = conn.recv(2056)
                    if data == SPECIAL_CHARS["interrupt"]:
                        break
                    elif SPECIAL_CHARS["interrupt"] in data:
                        data.strip(SPECIAL_CHARS["interrupt"])
                        f.write(data)
                        break
                    f.write(data)
            print("done...")
            dest_path = os.path.join(".", "recv_files", file_name)
            AesUtil.decrypt_file(path, key, dest_path)
            os.remove(path)
            return "Success"
        except ConnectionError:
            self.socket.close()
            self.init_connection()
            return "Failed"
        except Exception as err:
            print(err)
            return "Failed"
